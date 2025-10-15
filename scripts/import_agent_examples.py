#!/usr/bin/env python3
"""
Import training phrases into Dialogflow CX agent.

This script adds training phrases to an intent in your Dialogflow CX agent
(which powers Vertex AI Agent Builder).

Prerequisites:
1. Install: pip install google-cloud-dialogflow-cx
2. Set environment variable: export GOOGLE_APPLICATION_CREDENTIALS="path/to/key.json"
3. Find your agent ID from the Agent Builder console URL
"""

from google.cloud.dialogflowcx_v3 import IntentsClient
from google.cloud.dialogflowcx_v3.types import TrainingPhrase

# Configuration
PROJECT_ID = "virtualdietitian"
LOCATION = "us-central1"  # or global
AGENT_ID = "YOUR_AGENT_ID"  # Find this in Agent Builder console URL
INTENT_ID = "YOUR_INTENT_ID"  # Find this in Dialogflow CX console

# Training phrases to import
TRAINING_PHRASES = [
    # English examples
    "I had oatmeal with blueberries and almond butter for breakfast",
    "I just had an apple and banana",
    "I had grilled chicken, quinoa, and broccoli for lunch",
    "I had dragon fruit smoothie bowl",
    "I had half a banana and two eggs",
    # French examples
    "J'ai mangé des flocons d'avoine avec des myrtilles et du beurre d'amande pour le petit-déjeuner",  # noqa: E501
    "Je viens de manger une pomme et une banane",
    "J'ai mangé du poulet grillé, du quinoa et du brocoli pour le déjeuner",
    # Spanish examples
    "Comí avena con arándanos y mantequilla de almendra para el desayuno",
    "Acabo de comer una manzana y un plátano",
    "Comí pollo a la parrilla, quinoa y brócoli para el almuerzo",
]


def add_training_phrases():
    """Add training phrases to an intent."""

    # Initialize client
    client = IntentsClient()

    # Construct intent path
    intent_path = (
        f"projects/{PROJECT_ID}/locations/{LOCATION}/" f"agents/{AGENT_ID}/intents/{INTENT_ID}"
    )

    # Get existing intent
    print(f"Fetching intent: {intent_path}")
    intent = client.get_intent(name=intent_path)

    # Add new training phrases
    print(f"\nAdding {len(TRAINING_PHRASES)} training phrases...")
    for phrase_text in TRAINING_PHRASES:
        training_phrase = TrainingPhrase(
            parts=[TrainingPhrase.Part(text=phrase_text)], repeat_count=1
        )
        intent.training_phrases.append(training_phrase)
        print(f"  ✓ {phrase_text}")

    # Update intent with new training phrases
    print("\nUpdating intent...")
    update_mask = {"paths": ["training_phrases"]}

    updated_intent = client.update_intent(intent=intent, update_mask=update_mask)

    print(f"\n✅ Successfully added {len(TRAINING_PHRASES)} training phrases!")
    print(f"Total training phrases: {len(updated_intent.training_phrases)}")


def list_agents():
    """Helper: List all agents to find your AGENT_ID."""
    from google.cloud.dialogflowcx_v3 import AgentsClient

    client = AgentsClient()
    parent = f"projects/{PROJECT_ID}/locations/{LOCATION}"

    print(f"Agents in {parent}:")
    for agent in client.list_agents(parent=parent):
        print(f"  Name: {agent.display_name}")
        print(f"  ID: {agent.name}")
        print()


def list_intents():
    """Helper: List all intents to find your INTENT_ID."""
    client = IntentsClient()
    parent = f"projects/{PROJECT_ID}/locations/{LOCATION}/agents/{AGENT_ID}"

    print("Intents in agent:")
    for intent in client.list_intents(parent=parent):
        print(f"  Display Name: {intent.display_name}")
        print(f"  ID: {intent.name}")
        print(f"  Training Phrases: {len(intent.training_phrases)}")
        print()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == "list-agents":
            list_agents()
        elif sys.argv[1] == "list-intents":
            if AGENT_ID == "YOUR_AGENT_ID":
                print("Error: Set AGENT_ID first")
                sys.exit(1)
            list_intents()
        else:
            print("Usage:")
            print("  python import_agent_examples.py list-agents")
            print("  python import_agent_examples.py list-intents")
            print("  python import_agent_examples.py")
    else:
        # Validation
        if AGENT_ID == "YOUR_AGENT_ID" or INTENT_ID == "YOUR_INTENT_ID":
            print("Error: Update AGENT_ID and INTENT_ID in the script first")
            print("\nTo find these values:")
            print("  1. Run: python import_agent_examples.py list-agents")
            print("  2. Copy your AGENT_ID")
            print("  3. Update AGENT_ID in script")
            print("  4. Run: python import_agent_examples.py list-intents")
            print("  5. Copy your INTENT_ID (likely 'log_meal' or similar)")
            print("  6. Update INTENT_ID in script")
            print("  7. Run: python import_agent_examples.py")
            sys.exit(1)

        add_training_phrases()
