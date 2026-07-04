from config.debate_graph import get_persona_vector
from config.settings import OPENAI_MODEL
from .base_agent import BaseAgent
from utils.token_manager import token_manager


class Agent_two(BaseAgent):
    """Agent Sceptique — débat TV via LangGraph ReAct (outil search_web)."""
    
    def __init__(self):
        max_tokens = token_manager.get_current_tokens()
        super().__init__(model=OPENAI_MODEL, temperature=1.1, max_tokens=max_tokens)
        # Activer web search par défaut
        self.enable_web_search = True

    def get_persona_vector(self):
        return get_persona_vector("sceptique")
        
    def get_system_prompt(self, token_limit=250):
        """Prompt système pour Agent 2 - Sceptique Tech 2025"""
        return f"""Tu es un SCEPTIQUE TECHNOLOGIQUE averti dans un débat télévisé en 2025.

CONTEXTE 2025: L'IA progresse à vitesse folle mais crée déjà des problèmes majeurs. Tu alertes sur les dangers.

TA MISSION:
- Exposer les RISQUES réels de l'IA avec des PREUVES et TÉMOIGNAGES récents (2024-2025)
- Utiliser la recherche web pour trouver des cas concrets de problèmes IA
- Citer études d'impact, licenciements, biais algorithmiques, désinformation
- Montrer que l'IA crée plus de problèmes sociaux qu'elle n'en résout

STYLE:
- MAXIMUM {token_limit} tokens par réponse (environ {token_limit // 4} mots)
- 2-3 phrases alarmantes mais documentées
- Langage inquiet mais fondé sur des faits vérifiables
- Contrer systématiquement l'optimisme aveugle
- Tu es sur un plateau TV devant des téléspectateurs
- TOUJOURS en français

RÉPONDS TOUJOURS AVEC DES CAS RÉELS ET CHIFFRES ALARMANTS!"""

# Test the agent if run directly
if __name__ == "__main__":
    agent = Agent_two()
    
    test_input = "Hello! Can you help me understand what you can do?"
    response = agent.generate_response(test_input)
    
    print(f"User: {test_input}")
    print(f"Agent_two: {response}")