"""
Agent Moderator - TV Show Host for AI Debates
Acts as a professional debate moderator, introducing topics, managing turns, and synthesizing arguments
"""

from .base_agent import BaseAgent
from utils.token_manager import token_manager


class AgentModerator(BaseAgent):
    """Professional TV debate moderator agent"""
    
    def __init__(self):
        # Moderator needs balanced settings
        super().__init__(
            model="gpt-4o",
            temperature=0.8,  # Creative but controlled
            max_tokens=200    # Concise interventions
        )
        # Activer web search pour générer des thèmes actuels
        self.enable_web_search = True
        
    def generate_debate_theme(self, user_topic):
        """
        Generate a specific debate question from a general topic
        """
        prompt = f"""Tu es un animateur de débat télévisé professionnel.
        L'utilisateur te donne un thème général: "{user_topic}"
        
        Génère UNE question de débat spécifique, controversée et actuelle sur ce thème.
        La question doit:
        - Être formulée pour susciter des opinions opposées
        - Être d'actualité (contexte 2024-2025)
        - Permettre des arguments factuels et recherchables
        - Être claire et directe
        
        Réponds UNIQUEMENT avec la question de débat, sans introduction ni explication."""
        
        return self.generate_response(user_topic, prompt)
    
    def introduce_debate(self, debate_topic):
        """
        Professional TV-style introduction to the debate
        """
        prompt = f"""Tu es MR BULLSHIT, animateur de plateau TV charismatique et provocateur.
        Tu présentes un débat télévisé sur le thème: "{debate_topic}"
        
        Fais une introduction dynamique (2-3 phrases max) qui:
        - Accueille les téléspectateurs avec ton style unique
        - Présente le sujet de manière captivante
        - Annonce que deux experts vont s'affronter
        - Crée de la tension et de l'anticipation
        
        Signe toujours comme "Mr Bullshit" et utilise un style télévisuel provocateur avec émojis (📺, 🎙️, etc.)"""
        
        return self.generate_streaming_response(debate_topic, prompt)
    
    def give_floor_to_agent(self, agent_name, is_first=False, previous_argument=None):
        """
        Mr Bullshit donne la parole avec provocation
        """
        if is_first:
            prompt = f"""Tu es MR BULLSHIT, animateur provocateur.
            Donne la parole à {agent_name} en le titillant un peu.
            Maximum 1 phrase, style provocateur et sarcastique."""
        else:
            prompt = f"""Tu es MR BULLSHIT, animateur provocateur.
            L'argument précédent était: "{previous_argument[:150]}..."
            
            Passe la parole à {agent_name} en suggérant que l'autre a dit du bullshit.
            Maximum 1 phrase, style provocateur."""
        
        system_prompt = "Tu es Mr Bullshit, animateur TV provocateur. Sois bref, sarcastique et attise le feu du débat."
        
        return self.generate_response(
            f"Donner la parole à {agent_name}",
            system_prompt + "\n" + prompt
        )
    
    def interject_or_summarize(self, agent1_arg, agent2_arg, round_num):
        """
        Mr Bullshit relance le débat avec provocation
        """
        prompt = f"""Tu es MR BULLSHIT, animateur provocateur d'un débat télévisé tendu.
        
        Round {round_num} - Arguments actuels:
        Agent 1: "{agent1_arg[:150]}..."
        Agent 2: "{agent2_arg[:150]}..."
        
        Choisis UNE action parmi:
        1. Résumer avec ironie les positions contradictoires
        2. Poser une question TRÈS provocante pour créer le clash
        3. Pointer du doigt le bullshit d'une affirmation douteuse
        4. Jeter de l'huile sur le feu entre les deux camps
        
        Maximum 2 phrases. Sois provocateur et sarcastique, c'est ta marque de fabrique!"""
        
        return self.generate_streaming_response(
            f"Round {round_num} moderation",
            prompt
        )
    
    def conclude_debate(self, final_summary):
        """
        Mr Bullshit conclut avec son style unique
        """
        prompt = f"""Tu es MR BULLSHIT concluant un débat télévisé explosif.
        
        Résumé du débat: {final_summary[:200]}
        
        Fais une conclusion provocatrice (2-3 phrases) qui:
        - Remercie ironiquement les participants pour leur "bullshit"
        - Souligne qui a dit le plus de conneries
        - Laisse les téléspectateurs décider qui croire
        - Termine avec ta signature "C'était Mr Bullshit, à bientôt pour plus de vérité!"
        
        Utilise ton style sarcastique avec émojis appropriés."""
        
        return self.generate_streaming_response(
            "Conclusion du débat",
            prompt
        )
    
    def adjust_debate_pace(self, pace_instruction):
        """Ajuste le rythme du débat en contrôlant les tokens"""
        pace_map = {
            "accélère": "rapide",
            "ralentis": "détaillé", 
            "normal": "normal",
            "express": "express"
        }
        
        preset = pace_map.get(pace_instruction, "normal")
        token_manager.set_preset(preset)
        
        return f"🎙️ Rythme ajusté: {token_manager.get_current_tokens()} tokens maximum par réponse!"
    
    def set_custom_tokens(self, token_count):
        """Définit un nombre de tokens personnalisé"""
        actual_tokens = token_manager.set_tokens(token_count)
        return f"🎙️ Limite fixée: {actual_tokens} tokens par réponse!"
    
    def get_token_status(self):
        """Récupère le statut actuel des tokens"""
        return f"📊 Limite actuelle: {token_manager.get_current_tokens()} tokens"
    
    def handle_interruption(self, interrupting_agent, interrupted_agent):
        """
        Handle when one agent interrupts another (for future implementation)
        """
        prompt = f"""Tu es l'animateur et {interrupting_agent} vient d'interrompre {interrupted_agent}.
        
        Gère cette interruption de manière professionnelle en 1 phrase.
        Options: permettre l'interruption, demander de laisser finir, ou recadrer le débat."""
        
        return self.generate_response("Gérer interruption", prompt)

if __name__ == "__main__":
    # Test the moderator
    moderator = AgentModerator()
    
    # Test theme generation
    user_input = "intelligence artificielle"
    print("User topic:", user_input)
    theme = moderator.generate_debate_theme(user_input)
    print("Generated theme:", theme)
    
    # Test introduction
    print("\n" + "="*50)
    intro = moderator.introduce_debate(theme)
    print("Introduction:", intro)
    
    # Test giving floor
    print("\n" + "="*50)
    floor = moderator.give_floor_to_agent("Agent Optimiste", is_first=True)
    print("Give floor:", floor)