# AI/ML Project Template

Professional template for AI agent and ML projects with clean architecture, Docker support, and development best practices.

## Quick Start

### Prerequisites
- Python 3.11+

### Initial Setup

1. **Clone and customize:**
   ```bash
   git clone https://github.com/adamkwhite/project_template my-ai-project
   cd my-ai-project
   # Update project name in pyproject.toml, docker-compose.yaml
   ```

2. **Environment configuration:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys (OpenAI, LangSmith, etc.)
   ```

3. **Install dependencies:**
   ```bash
   # Production dependencies
   pip install -r requirements.txt

   # Development dependencies (testing, linting, formatting)
   pip install -r requirements-dev.txt
   ```

4. **Run with Docker:**
   ```bash
   docker-compose up --build
   ```

## Project Structure

```
project_template/
├── .github/
│   └── workflows/              # CI/CD pipelines (pytest, Docker build)
│
├── .claude/                    # Claude AI custom commands
│   ├── commands/
│   │   ├── StartOfTheDay.md
│   │   └── WrapUpForTheDay.md
│   └── settings.local.json
│
├── src/
│   └── your_agent/
│       ├── __init__.py
│       ├── config.py           # Global configuration
│       │
│       ├── domain/             # DOMAIN LAYER - Business logic
│       │   ├── __init__.py
│       │   ├── models.py       # Pydantic models, state definitions
│       │   ├── exceptions.py   # Custom exceptions
│       │   ├── tools/          # Custom tools/functions
│       │   ├── prompts/        # Prompt templates
│       │   └── utils.py        # Shared utilities
│       │
│       ├── application/        # APPLICATION LAYER - Orchestration
│       │   ├── __init__.py
│       │   ├── agents/         # Agent workflows
│       │   │   ├── chat_agent.py
│       │   │   ├── research_agent.py
│       │   │   └── task_agent.py
│       │   └── chains/         # Reusable processing chains
│       │
│       └── infrastructure/     # INFRASTRUCTURE LAYER - External services
│           ├── __init__.py
│           ├── api/            # REST/GraphQL endpoints
│           │   └── main.py     # FastAPI/Flask app
│           ├── llm/            # LLM provider clients
│           ├── storage/        # Database/vector store
│           └── monitoring/     # Logging/observability
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # Pytest fixtures
│   ├── unit/                   # Fast unit tests (no external deps)
│   ├── integration/            # Integration tests (testcontainers)
│   └── e2e/                    # End-to-end workflow tests
│
├── docs/
│   ├── architecture.md         # System design decisions
│   ├── deployment.md           # AWS/GCP deployment guides
│   └── ai-docs/                # AI-assisted development guides
│       ├── generate-tasks.md
│       ├── create-prd.md
│       └── process-task-list.md
│
├── scripts/
│   ├── setup.sh                # Initial environment setup
│   ├── build.sh                # Docker build automation
│   └── deploy.sh               # Deployment scripts
│
├── data/                       # Local data files (gitignored)
├── notebooks/                  # Jupyter notebooks for experiments
│
├── .env.example                # Environment variable template
├── .gitignore
├── CLAUDE.md                   # Project context for Claude AI
├── docker-compose.yaml
├── Dockerfile
├── Makefile                    # Build/run shortcuts
├── pyproject.toml              # Python project config
├── requirements.txt            # Production dependencies
├── requirements-dev.txt        # Development dependencies
├── LICENSE
└── README.md
```

## Architecture Overview

### Three-Layer Design

**Domain Layer** (`src/your_agent/domain/`)
- Core business logic and rules
- Framework-agnostic (no LangChain/LangGraph coupling)
- Custom tools, prompts, state models
- Pure Python, highly testable

**Application Layer** (`src/your_agent/application/`)
- Workflow orchestration (agents, chains, graphs)
- Coordinates domain logic
- Handles agent-to-agent communication
- Can use LangChain, LangGraph, or custom frameworks

**Infrastructure Layer** (`src/your_agent/infrastructure/`)
- External service integrations (LLMs, databases, APIs)
- API endpoints (FastAPI/Flask)
- Monitoring and observability
- Deployment-specific code

### Understanding Domain vs Application

**Domain Layer = "What your agent knows"**

Business logic independent of any framework. Examples:

```python
# domain/tools/calculator.py
def calculate_mortgage(principal: float, rate: float, years: int) -> float:
    """Pure business logic - no LLM, no LangChain"""
    monthly_rate = rate / 12 / 100
    num_payments = years * 12
    return principal * (monthly_rate * (1 + monthly_rate)**num_payments) / \
           ((1 + monthly_rate)**num_payments - 1)

# domain/models.py
from pydantic import BaseModel

class CustomerQuery(BaseModel):
    question: str
    customer_id: str
    priority: str

# domain/prompts/templates.py
MORTGAGE_ADVISOR_PROMPT = """You are a mortgage advisor.
Customer context: {customer_history}
Question: {question}
Provide clear, compliant advice."""
```

**Application Layer = "How your agent uses it"**

Framework-specific orchestration that ties domain logic together:

```python
# application/agents/mortgage_agent.py
from langgraph.graph import StateGraph
from domain.tools.calculator import calculate_mortgage
from domain.prompts.templates import MORTGAGE_ADVISOR_PROMPT

def build_mortgage_agent():
    """Uses domain logic in a LangGraph workflow"""
    graph = StateGraph()
    graph.add_node("calculate", lambda state: {
        "payment": calculate_mortgage(
            state["principal"],
            state["rate"],
            state["years"]
        )
    })
    # ... rest of workflow
```

**When to put code in Domain vs Application:**

Put in **Domain** if it's:
- Business rules (mortgage calculations, risk scoring)
- Data models (Pydantic models, state definitions)
- Custom tools that don't need LLM (parsers, validators, formatters)
- Prompt templates (just strings)
- Exceptions specific to your business (InvalidLoanAmount)
- Utilities (date formatting for your industry)

Put in **Application** if it's:
- Agent graphs/chains
- Routing logic between agents
- LLM-based decision making
- Workflow state machines
- Multi-agent coordination

**The test:** If you deleted LangChain/LangGraph tomorrow and switched to raw OpenAI, would this code still be useful?
- Yes → Domain
- No → Application

**Benefits:**
- Easy to test (mock external services)
- Swap frameworks without rewriting business logic
- Clear separation of concerns
- Scales from prototype to production

## Development Workflow

### Running Tests
```bash
# Unit tests (fast, no external dependencies)
pytest tests/unit -v

# Integration tests (uses Docker testcontainers)
pytest tests/integration -v

# All tests with coverage
pytest --cov=src --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Code Quality
```bash
# Format code
black src/ tests/

# Lint
ruff check src/ tests/

# Type checking
mypy src/
```

### Docker Development
```bash
# Build and run
docker-compose up --build

# Run specific service
docker-compose up agent-api

# Rebuild after dependency changes
docker-compose up --build --force-recreate

# View logs
docker-compose logs -f agent-api
```

### Makefile Shortcuts
```bash
make install      # Install dependencies
make test         # Run all tests
make lint         # Run linting and type checks
make format       # Format code with black
make docker-up    # Start Docker services
make docker-down  # Stop Docker services
make clean        # Clean cache files
```

## Environment Variables

Key variables in `.env`:

```bash
# LLM Provider
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Observability
LANGSMITH_API_KEY=ls_...
LANGSMITH_PROJECT=my-project

# Infrastructure
DATABASE_URL=postgresql://user:pass@localhost/db
REDIS_URL=redis://localhost:6379

# Application
LOG_LEVEL=INFO
ENVIRONMENT=development
```

## Deployment

### AWS EC2 (t2.small)
```bash
# 1. SSH into instance
ssh ubuntu@your-ec2-ip

# 2. Clone and setup
git clone <your-repo> && cd <repo>
cp .env.example .env
# Edit .env with production values

# 3. Run with Docker
docker-compose -f docker-compose.prod.yaml up -d
```

See `docs/deployment.md` for detailed AWS, GCP, Azure guides.

## Project Customization Checklist

When starting a new project from this template:

- [ ] Update `pyproject.toml` with project name
- [ ] Rename `src/your_agent/` to actual project name
- [ ] Update `docker-compose.yaml` service names
- [ ] Configure `.env` with actual API keys
- [ ] Update README title and description
- [ ] Add project-specific docs to `docs/`
- [ ] Configure CI/CD in `.github/workflows/`
- [ ] Update `CLAUDE.md` with project context
- [ ] Update `LICENSE` file

## Git Configuration

Default branch: `main`
GitHub user: `adamkwhite`

## License

MIT License - See [LICENSE](LICENSE)
