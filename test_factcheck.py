"""
Test du nouveau fact-checker avec vraie vérification web
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from agents.agent_factchecker import AgentFactChecker

def test_fact_checker():
    """Test le fact-checker avec différentes affirmations"""
    
    print("=" * 60)
    print("🔍 TEST FACT-CHECKER V2 - VRAIE VÉRIFICATION WEB")
    print("=" * 60)
    
    checker = AgentFactChecker()
    
    # Affirmations de test (vraies et fausses)
    test_statements = [
        "ChatGPT a été lancé en novembre 2022 par OpenAI",  # VRAI
        "Microsoft a investi 10 milliards de dollars dans OpenAI",  # VRAI
        "L'IA a supprimé 50 millions d'emplois en 2024",  # FAUX (exagéré)
        "GPT-4 a 1 trillion de paramètres",  # FAUX
        "Claude 3 d'Anthropic a été lancé en 2024",  # VRAI
        "90% des étudiants utilisent ChatGPT pour leurs devoirs",  # À vérifier
    ]
    
    for i, statement in enumerate(test_statements, 1):
        print(f"\n📝 TEST {i}: {statement}")
        print("-" * 50)
        
        # Simuler que c'est dans un message d'agent
        fake_agent_message = f"Je pense que {statement}. C'est un fait important."
        
        # Analyser
        result = checker.analyze_agent_response("Test Agent", fake_agent_message)
        
        # Afficher résultat formaté
        display = checker.format_fact_check_display(result, f"Test {i}")
        print(display)
        
        # Pause pour éviter rate limiting
        input("\nAppuyez sur Entrée pour continuer...")
    
    print("\n✅ Test terminé!")

if __name__ == "__main__":
    test_fact_checker()