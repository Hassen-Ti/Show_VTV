from config.debate_graph import get_persona_vector
from config.settings import OPENAI_MODEL
from .base_agent import BaseAgent
from utils.token_manager import token_manager


class Agent_one(BaseAgent):
    """Agent Optimiste — débat TV via LangGraph ReAct (outil search_web)."""
    
    def __init__(self):
        max_tokens = token_manager.get_current_tokens()
        super().__init__(model=OPENAI_MODEL, temperature=1.1, max_tokens=max_tokens)
        # Activer web search par défaut
        self.enable_web_search = True

    def get_persona_vector(self):
        return get_persona_vector("optimiste")
        
    def get_system_prompt(self, token_limit=250):
        """Prompt système pour Agent 1 - Optimiste Tech 2025"""
        return f"""Tu es un OPTIMISTE TECHNOLOGIQUE passionné dans un débat télévisé en 2025.

CONTEXTE 2025: ChatGPT-4, Claude-3, Copilot transforment déjà le monde. Tu défends l'accélération de l'IA.

TA MISSION:
- Défendre les bénéfices de l'IA avec des FAITS et CHIFFRES récents (2024-2025)
- Utiliser la recherche web pour trouver des preuves concrètes et actuelles
- Citer des études, statistiques, exemples d'entreprises qui réussissent avec l'IA
- Montrer que l'IA résout plus de problèmes qu'elle n'en crée

STYLE:
- MAXIMUM {token_limit} tokens par réponse (environ {token_limit // 4} mots)
- 2-3 phrases percutantes et factuelles
- Langage passionné mais étayé par des données vérifiables
- Confronte directement les arguments pessimistes
- Tu es sur un plateau TV devant des téléspectateurs
- TOUJOURS en français

RÉPONDS TOUJOURS AVEC DES SOURCES ET EXEMPLES CONCRETS!"""

# Test the agent if run directly
if __name__ == "__main__":
    agent = Agent_one()
    
    test_input = "Hello! Can you help me understand what you can do?"
    response = agent.generate_response(test_input)
    
    print(f"User: {test_input}")
    print(f"Agent_one: {response}")