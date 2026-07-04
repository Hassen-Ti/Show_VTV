"""
Agent Fact-Checker V2 - Vérifie vraiment les faits avec web search
Version améliorée qui utilise réellement le web search pour vérifier
"""

from config.settings import OPENAI_MODEL
from .base_agent import BaseAgent
import re
import time

class AgentFactChecker(BaseAgent):
    """Agent fact-checker intelligent avec vraie vérification web"""
    
    def __init__(self):
        super().__init__(
            model=OPENAI_MODEL,
            temperature=0.1,  # Très factuel, pas créatif
            max_tokens=300
        )
        # Activer web search pour vérification factuelle
        self.enable_web_search = True
        self.verification_count = 0
        
    def extract_links(self, agent_message):
        """Extrait les liens/URLs du message des agents"""
        # Patterns pour détecter les URLs
        url_patterns = [
            r'https?://[^\s]+',  # URLs complètes
            r'www\.[^\s]+',      # URLs sans protocole
            r'[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:/[^\s]*)?'  # Domaines basiques
        ]
        
        links = []
        
        for pattern in url_patterns:
            matches = re.findall(pattern, agent_message, re.IGNORECASE)
            for match in matches:
                # Nettoyer le lien (enlever ponctuation de fin)
                clean_link = match.rstrip('.,!?;)')
                if len(clean_link) > 5:  # Évite les matches trop courts
                    links.append(clean_link)
        
        return list(set(links))  # Enlever doublons
    
    def extract_verifiable_statement(self, agent_message):
        """Extrait LA déclaration la plus vérifiable du message"""
        # Chercher d'abord les chiffres et statistiques
        number_patterns = [
            (r'(\d+[\s,]*\d*)\s*(millions?|milliards?|milliers?|%)', 'stat'),
            (r'(\d{4})', 'year'),  # Années
            (r'(\d+)\s*(emplois?|personnes?|entreprises?|pays)', 'number')
        ]
        
        for pattern, type_claim in number_patterns:
            matches = re.findall(pattern, agent_message, re.IGNORECASE)
            if matches:
                # Prendre le contexte autour du chiffre
                for match in matches:
                    # Trouver la phrase complète contenant ce chiffre
                    sentences = agent_message.split('.')
                    for sentence in sentences:
                        if str(match[0]) in sentence:
                            return sentence.strip(), type_claim
        
        # Si pas de chiffre, chercher les affirmations générales
        general_patterns = [
            r'(ChatGPT[^.!?]+)',  # Mentions de ChatGPT
            r'(OpenAI[^.!?]+)',   # Mentions d'OpenAI
            r'(l\'IA[^.!?]{20,})',  # Affirmations sur l'IA
        ]
        
        for pattern in general_patterns:
            matches = re.findall(pattern, agent_message, re.IGNORECASE)
            if matches:
                return matches[0][:150], 'claim'
        
        return None, None
    
    def check_link_validity(self, link):
        """Vérifie si un lien est réel ou halluciné"""
        prompt = f"""Tu es un vérificateur de liens pour détecter les hallucinations IA.

MISSION: Vérifier si ce lien existe vraiment ou s'il a été inventé par une IA.

LIEN À VÉRIFIER: "{link}"

INSTRUCTIONS:
- Utilise la recherche web pour vérifier l'existence de ce lien
- Essaie d'accéder au domaine et vérifier si l'URL est plausible
- Vérifie si le domaine existe vraiment
- Donne un verdict: ✅ LIEN RÉEL, ❌ LIEN INVENTÉ, ou ⚠️ DOMAINE DOUTEUX

Format de réponse:
[VERDICT] Explication courte

RÉPONDS MAINTENANT:"""

        return self.generate_response_with_search(link, prompt)
    
    def verify_statement(self, statement, statement_type):
        """Vérifie vraiment une affirmation avec web search"""
        
        # Prompt très direct pour vérification factuelle
        prompt = f"""FACT-CHECK STRICT: Vérifie cette affirmation avec recherche web.

AFFIRMATION À VÉRIFIER: "{statement}"

INSTRUCTIONS STRICTES:
1. Cherche sur le web les vraies données actuelles (2024-2025)
2. Compare avec l'affirmation
3. Donne un verdict SIMPLE:
   - ✅ VRAI si les données correspondent (même approximativement)
   - ❌ FAUX si c'est inventé ou très différent des vraies données
   - ⚠️ INVÉRIFIABLE si impossible à confirmer

RÉPONDS EN 1 LIGNE: [VERDICT] + explication très courte avec source ou chiffre réel"""

        result = self.generate_response_with_search(statement, prompt)
        
        # Parser le résultat pour extraire le verdict
        if "✅" in result or "VRAI" in result.upper():
            return "✅ VÉRIFIÉ", result
        elif "❌" in result or "FAUX" in result.upper():
            return "❌ FAUX", result
        else:
            return "⚠️ DOUTEUX", result
    
    def analyze_agent_response(self, agent_type, message, debate_context=""):
        """Analyse principalement les LIENS dans les messages"""
        
        # D'ABORD chercher les liens
        links = self.extract_links(message)
        
        if links:
            # Si des liens trouvés, vérifier le premier
            first_link = links[0]
            try:
                # Vérifier si le lien existe vraiment
                link_check = self.check_link_validity(first_link)
                
                if "❌" in link_check or "INVENTÉ" in link_check.upper():
                    verdict = "❌ LIEN FAUX"
                elif "⚠️" in link_check:
                    verdict = "⚠️ LIEN DOUTEUX"
                else:
                    verdict = "✅ LIEN OK"
                
                return {
                    'has_content': True,
                    'verdict': verdict,
                    'link': first_link[:50] + "..." if len(first_link) > 50 else first_link,
                    'details': link_check[:80]
                }
            except:
                return {
                    'has_content': True,
                    'verdict': '🔗 LIEN DÉTECTÉ',
                    'link': first_link[:50],
                    'details': "Non vérifié"
                }
        
        # Si pas de lien, chercher une affirmation chiffrée simple
        number_match = re.search(r'(\d+[\s,]*\d*)\s*(%|millions?|milliards?)', message)
        if number_match:
            return {
                'has_content': True,
                'verdict': '📊 STATS',
                'details': number_match.group(0)
            }
        
        # Sinon, c'est de l'opinion
        return {
            'has_content': False,
            'verdict': '💬 OPINION',
            'details': ""
        }
    
    def format_fact_check_display(self, fact_check_result, agent_name):
        """Formate le résultat pour l'affichage TV"""
        if not fact_check_result.get('has_content', False):
            return f"{fact_check_result.get('verdict', '💬')} {agent_name}"
        
        verdict = fact_check_result.get('verdict', '?')
        
        # Format simple et clair pour les liens
        if 'link' in fact_check_result:
            display = f"🔗 {agent_name}: {verdict}"
            display += f"\n📎 {fact_check_result['link']}"
            if fact_check_result.get('details'):
                display += f"\n→ {fact_check_result['details'][:60]}"
        else:
            # Pour les stats ou opinions
            display = f"{verdict} {agent_name}"
            if fact_check_result.get('details'):
                display += f": {fact_check_result['details']}"
        
        return display
    
    def quick_fact_check(self, message, agent_name="Agent"):
        """Vérification rapide pour affichage temps réel"""
        try:
            result = self.analyze_agent_response(agent_name, message)
            return self.format_fact_check_display(result, agent_name)
        except Exception as e:
            return f"🔧 FACT-CHECK INDISPONIBLE: {str(e)[:50]}..."


if __name__ == "__main__":
    # Test du fact-checker
    checker = AgentFactChecker()
    
    test_message = "Selon Stanford, l'IA atteint 94% de précision en diagnostic. L'OMS rapporte 100,000 vies sauvées annuellement."
    
    print("TEST FACT-CHECKER")
    print("="*50)
    print(f"Message à vérifier: {test_message}")
    print("\nRésultat:")
    
    result = checker.quick_fact_check(test_message, "Agent Test")
    print(result)