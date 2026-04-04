"""
Virtual Dietitian FastAPI backend.
Replaces GCP Vertex AI Agent Builder with OpenRouter (Gemini Flash) + existing nutrition pipeline.
"""

import json
import os
import sys
from pathlib import Path

# Add nutrition-analyzer to path so we can import its modules directly
NUTRITION_DIR = Path(__file__).resolve().parent.parent / "cloud-functions" / "nutrition-analyzer"
sys.path.insert(0, str(NUTRITION_DIR))

from dotenv import load_dotenv  # noqa: E402
from fastapi import FastAPI  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402

# These imports resolve from cloud-functions/nutrition-analyzer/
from main import ENABLE_CNF_API, ENABLE_USDA_API, parse_meal_description  # noqa: E402
from nutrition_calculator import calculate_nutrition  # noqa: E402
from openai import OpenAI  # noqa: E402
from pydantic import BaseModel  # noqa: E402
from rule_engine import apply_rules  # noqa: E402

load_dotenv()

app = FastAPI(title="Virtual Dietitian API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
)

MODEL = os.getenv("OPENROUTER_MODEL", "google/gemini-2.0-flash-001")

SYSTEM_PROMPT = """\
You are a Virtual Dietitian AI assistant. You help users analyze \
meals and provide nutritional feedback.

When a user describes a meal or food they ate, use the analyze_meal \
tool with their meal description.
When greeting or asking general nutrition questions, respond directly.

Be friendly, encouraging, and concise. Match the user's language (English, French, or Spanish).

After receiving nutrition analysis results, present them in this format:

**Nutritional Summary:**
- Calories: [calories] cal
- Protein: [protein_g]g ([protein_pct]%)
- Carbs: [carbs_g]g ([carbs_pct]%)
- Fat: [fat_g]g ([fat_pct]%)
- Fiber: [fiber_g]g
- Sodium: [sodium_mg]mg

**Insights:**
[List each insight message]

End with a relevant follow-up question."""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "analyze_meal",
            "description": "Analyze the nutritional content of a meal described by the user",
            "parameters": {
                "type": "object",
                "properties": {
                    "meal_description": {
                        "type": "string",
                        "description": "The meal description",
                    }
                },
                "required": ["meal_description"],
            },
        },
    }
]


class ChatRequest(BaseModel):
    message: str
    history: list[dict] = []


def run_nutrition_pipeline(meal_description: str) -> dict:
    """Run the existing nutrition analysis pipeline."""
    food_items = parse_meal_description(meal_description)
    if not food_items:
        return {
            "error": "Could not identify any foods in your description. Try being more specific."
        }

    nutrition_result = calculate_nutrition(
        food_items,
        use_cnf_fallback=ENABLE_CNF_API,
        use_usda_fallback=ENABLE_USDA_API,
    )
    insights = apply_rules(
        nutrition_result["total_nutrition"],
        nutrition_result["macro_percentages"],
        nutrition_result.get("food_categories", []),
    )
    return {
        "foods_detected": [f["name"] for f in food_items],
        "total_nutrition": nutrition_result["total_nutrition"],
        "macro_percentages": nutrition_result["macro_percentages"],
        "insights": insights,
        "unknown_foods": nutrition_result.get("unknown_foods", []),
    }


@app.post("/api/chat")
async def chat(req: ChatRequest):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    # Keep last 20 messages for context
    messages.extend(req.history[-20:])
    messages.append({"role": "user", "content": req.message})

    # Phase 1: LLM decides whether to call tool or respond directly
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=TOOLS,
        tool_choice="auto",
    )

    msg = response.choices[0].message

    # If LLM wants to call the nutrition analyzer
    if msg.tool_calls:
        tool_call = msg.tool_calls[0]
        args = json.loads(tool_call.function.arguments)
        meal_desc = args.get("meal_description", req.message)

        tool_result = run_nutrition_pipeline(meal_desc)

        # Phase 2: Send tool result back to LLM for natural language formatting
        messages.append(msg.model_dump())
        messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(tool_result),
            }
        )

        final = client.chat.completions.create(model=MODEL, messages=messages)
        return {"reply": final.choices[0].message.content}

    # Direct response (greeting, question, etc.)
    return {"reply": msg.content}


@app.get("/api/health")
async def health():
    return {"status": "ok"}
