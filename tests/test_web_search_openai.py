"""
Test minimal : recherche web via l’API Responses OpenAI (clé dans `.env`).
"""
import os
from openai import OpenAI
from dotenv import load_dotenv


def test_web_search_simple():
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Erreur: OPENAI_API_KEY absente du fichier .env")
        return

    print(f"API Key chargée: {api_key[:20]}...")
    client = OpenAI(api_key=api_key)
    print("Test web search — taper 'quit' pour sortir.")

    while True:
        question = input("\nQuestion (ou quit): ").strip()
        if question.lower() in ("quit", "exit", "q"):
            break
        if not question:
            continue
        print("Recherche en cours...")
        try:
            response = client.responses.create(
                model="gpt-4o",
                tools=[{"type": "web_search_preview"}],
                input=question,
            )
            print(response.output_text)
        except Exception as e:
            print(f"Erreur: {e}")


if __name__ == "__main__":
    test_web_search_simple()
