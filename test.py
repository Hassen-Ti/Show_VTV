"""
Test simple du web search OpenAI avec Responses API
Juste pour voir si ça marche vraiment
"""
import os
from openai import OpenAI
from dotenv import load_dotenv

def test_web_search_simple():
    """Test basique web search avec GPT-4o"""
    
    # Charger les variables d'environnement depuis .env
    load_dotenv()
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Erreur: OPENAI_API_KEY non trouvée dans .env")
        return
    
    print(f"✅ API Key chargée: {api_key[:20]}...")
    
    client = OpenAI(api_key=api_key)
    
    print("=" * 60)
    print("🔍 TEST WEB SEARCH SIMPLE - GPT-4O")
    print("=" * 60)
    
    while True:
        # Demander une question à l'utilisateur
        question = input("\n❓ Posez votre question (ou 'quit' pour sortir): ")
        
        if question.lower() in ['quit', 'exit', 'q']:
            break
        
        print("\n🔍 Recherche en cours...")
        
        try:
            # Utiliser Responses API avec web_search_preview (syntax correcte!)
            response = client.responses.create(
                model="gpt-4o",
                tools=[{"type": "web_search_preview"}],
                input=question
            )
            
            print("\n🤖 RÉPONSE:")
            print("-" * 40)
            print(response.output_text)
            print("-" * 40)
            
        except Exception as e:
            print(f"❌ Erreur: {e}")
    
    print("\n✅ Test terminé!")

if __name__ == "__main__":
    test_web_search_simple()