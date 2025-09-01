"""
Backend Bridge Modernisé
- Historique complet pour tous les agents
- Délais entre réponses
- Fact-checker intégré
- Support personas et topics
"""

import sys
import time
from pathlib import Path

# Ajouter le répertoire src au path pour les imports
sys.path.insert(0, str(Path(__file__).parent))

from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, QThread
from agents.agent_1 import Agent_one
from agents.agent_2 import Agent_two
from agents.agent_moderator import AgentModerator
from agents.agent_factchecker import AgentFactChecker
from config.settings import *
from config.personas import get_persona, get_available_domains
from config.topics import get_topic_for_domain, format_topic_for_debate

# Import absolu avec fallback pour token_manager
try:
    from utils.token_manager import token_manager
except ImportError:
    # sys et Path déjà importés en haut
    sys.path.append(str(Path(__file__).parent))
    from utils.token_manager import token_manager

class AgentWorkerModern(QThread):
    """Worker thread modernisé avec historique et fact-checking"""
    
    messageStream = pyqtSignal(str, str, int)  # agent_type, content, round_num
    messageComplete = pyqtSignal(str, str, int)  # agent_type, full_message, round_num
    searchNotification = pyqtSignal(str, str)  # agent_type, search_info
    factCheckResult = pyqtSignal(str, str)  # agent_type, fact_check_result
    errorOccurred = pyqtSignal(str)
    finished = pyqtSignal()
    
    def __init__(self, agent_one, agent_two, moderator, fact_checker, topic, 
                 prompt_one, prompt_two, use_moderator=True):
        super().__init__()
        self.agent_one = agent_one
        self.agent_two = agent_two
        self.moderator = moderator
        self.fact_checker = fact_checker
        self.topic = topic
        self.prompt_one = prompt_one
        self.prompt_two = prompt_two
        self.use_moderator = use_moderator
        self.should_stop = False
        
        # Historique complet du débat
        self.debate_history = []
        
    def stop(self):
        """Arrêter le débat"""
        self.should_stop = True
    
    def add_to_history(self, round_num, agent_type, message, message_type="response"):
        """Ajouter message à l'historique"""
        self.debate_history.append({
            "round": round_num,
            "agent": agent_type,
            "message": message,
            "type": message_type,
            "timestamp": time.time()
        })
    
    def format_history_for_agent(self, current_agent):
        """Formate l'historique pour un agent spécifique"""
        if not self.debate_history:
            return ""
        
        history_text = "🎬 HISTORIQUE DU DÉBAT (pour référence):\n\n"
        
        for entry in self.debate_history[-8:]:  # Derniers 8 messages pour contexte
            agent_name = {
                "moderator": "🎙️ ANIMATEUR",
                "agent_one": "🔥 ADVERSAIRE" if current_agent == "agent_two" else "🔥 VOUS", 
                "agent_two": "💀 ADVERSAIRE" if current_agent == "agent_one" else "💀 VOUS"
            }.get(entry["agent"], entry["agent"])
            
            history_text += f"[Round {entry['round']}] {agent_name}: {entry['message']}\n\n"
        
        history_text += "🎯 RÉPONDEZ MAINTENANT en tenant compte de cet historique!\n"
        return history_text
    
    def stream_moderator_message(self, message, round_num=0):
        """Stream message modérateur avec historique"""
        for char in message:
            if self.should_stop:
                break
            self.messageStream.emit("moderator", char, round_num)
            time.sleep(0.02)  # Effet typing plus lent pour modérateur
        
        self.messageComplete.emit("moderator", message, round_num)
        self.add_to_history(round_num, "moderator", message, "moderation")
    
    def run(self):
        """Débat avec historique, délais et fact-checking"""
        try:
            # Introduction modérateur avec historique
            if self.use_moderator:
                intro = self.moderator.introduce_debate(self.topic)
                self.stream_moderator_message(intro, 0)
                
                if self.should_stop:
                    return
                
                # Délai après introduction
                time.sleep(DEBATE_CONFIG["moderator_delay_seconds"])
            
            # Boucle principale de débat
            for round_num in range(DEBATE_CONFIG["max_rounds"]):
                if self.should_stop:
                    break
                
                # === TOUR AGENT ONE ===
                
                # Modérateur donne la parole
                if self.use_moderator:
                    floor_msg = self.moderator.give_floor_to_agent(
                        "Agent One 🔥",
                        is_first=(round_num == 0),
                        previous_argument=self.debate_history[-1]["message"] if self.debate_history else None
                    )
                    self.stream_moderator_message(floor_msg, round_num + 1)
                    
                    if self.should_stop:
                        break
                    
                    time.sleep(1)  # Pause avant réponse agent
                
                # Agent One répond avec historique et tokens dynamiques
                history_context = self.format_history_for_agent("agent_one")
                current_tokens = token_manager.get_current_tokens()
                full_prompt = f"{self.agent_one.get_system_prompt(current_tokens)}\n\n{history_context}"
                
                agent_one_response = ""
                
                def stream_callback_one(chunk):
                    nonlocal agent_one_response
                    agent_one_response += chunk
                    self.messageStream.emit("agent_one", chunk, round_num + 1)
                
                def search_callback_one(search_info):
                    self.searchNotification.emit("agent_one", search_info)
                
                response_one = self.agent_one.generate_streaming_response_with_search(
                    self.topic if round_num == 0 else "Continuez le débat en répondant aux arguments précédents",
                    full_prompt,
                    stream_callback=stream_callback_one,
                    search_callback=search_callback_one
                )
                
                if response_one.startswith("Error:"):
                    self.errorOccurred.emit(f"Agent One: {response_one}")
                    return
                
                self.messageComplete.emit("agent_one", response_one, round_num + 1)
                self.add_to_history(round_num + 1, "agent_one", response_one)
                
                # Fact-check Agent One
                if self.fact_checker:
                    fact_result = self.fact_checker.quick_fact_check(response_one, "Agent 1 🔥")
                    self.factCheckResult.emit("agent_one", fact_result)
                
                if self.should_stop:
                    break
                
                # Délai pour lecture
                time.sleep(DEBATE_CONFIG["response_delay_seconds"])
                
                # === TOUR AGENT TWO ===
                
                # Modérateur donne la parole  
                if self.use_moderator:
                    floor_msg = self.moderator.give_floor_to_agent(
                        "Agent Two 💀",
                        is_first=False,
                        previous_argument=response_one
                    )
                    self.stream_moderator_message(floor_msg, round_num + 1)
                    
                    if self.should_stop:
                        break
                    
                    time.sleep(1)  # Pause avant réponse agent
                
                # Agent Two répond avec historique et tokens dynamiques
                history_context = self.format_history_for_agent("agent_two")
                current_tokens = token_manager.get_current_tokens()
                full_prompt = f"{self.agent_two.get_system_prompt(current_tokens)}\n\n{history_context}"
                
                agent_two_response = ""
                
                def stream_callback_two(chunk):
                    nonlocal agent_two_response
                    agent_two_response += chunk
                    self.messageStream.emit("agent_two", chunk, round_num + 1)
                
                def search_callback_two(search_info):
                    self.searchNotification.emit("agent_two", search_info)
                
                response_two = self.agent_two.generate_streaming_response_with_search(
                    response_one,  # Répond à Agent One
                    full_prompt,
                    stream_callback=stream_callback_two,
                    search_callback=search_callback_two
                )
                
                if response_two.startswith("Error:"):
                    self.errorOccurred.emit(f"Agent Two: {response_two}")
                    return
                
                self.messageComplete.emit("agent_two", response_two, round_num + 1)
                self.add_to_history(round_num + 1, "agent_two", response_two)
                
                # Fact-check Agent Two
                if self.fact_checker:
                    fact_result = self.fact_checker.quick_fact_check(response_two, "Agent 2 💀")
                    self.factCheckResult.emit("agent_two", fact_result)
                
                # Délai pour lecture
                time.sleep(DEBATE_CONFIG["response_delay_seconds"])
                
                # Intervention modérateur tous les 2 rounds
                if self.use_moderator and (round_num + 1) % 2 == 0 and round_num < DEBATE_CONFIG["max_rounds"] - 1:
                    if self.should_stop:
                        break
                    
                    interjection = self.moderator.interject_or_summarize(
                        response_one, response_two, round_num + 1
                    )
                    self.stream_moderator_message(interjection, round_num + 1)
                    time.sleep(DEBATE_CONFIG["moderator_delay_seconds"])
            
            # Conclusion modérateur
            if self.use_moderator and not self.should_stop:
                conclusion = self.moderator.conclude_debate(
                    f"Débat passionnant sur: {self.topic}"
                )
                self.stream_moderator_message(conclusion, DEBATE_CONFIG["max_rounds"] + 1)
            
            self.finished.emit()
            
        except Exception as e:
            self.errorOccurred.emit(f"Erreur worker: {str(e)}")


class BackendBridgeModern(QObject):
    """Backend modernisé avec personas, historique et fact-checking"""
    
    # Signaux pour QML
    messageStreamReceived = pyqtSignal(str, str, int)
    messageCompleted = pyqtSignal(str, str, int)
    searchStarted = pyqtSignal(str, str)
    factCheckUpdate = pyqtSignal(str, str)
    errorOccurred = pyqtSignal(str)
    debateFinished = pyqtSignal()
    debateStatusChanged = pyqtSignal(bool)
    themeGenerated = pyqtSignal(str)
    personasAvailable = pyqtSignal(list)
    
    def __init__(self):
        super().__init__()
        
        # Initialisation des agents
        try:
            self.agent_one = Agent_one()
            self.agent_two = Agent_two()
            self.moderator = AgentModerator()
            self.fact_checker = AgentFactChecker()
        except ValueError as e:
            print(f"Erreur initialisation agents: {e}")
            raise
        
        self.worker = None
        self.is_running = False
        self.current_domain = None
    
    @pyqtSlot(str)
    def generateTheme(self, user_topic):
        """Génère un thème de débat"""
        try:
            theme = self.moderator.generate_debate_theme(user_topic)
            self.themeGenerated.emit(theme)
        except Exception as e:
            self.errorOccurred.emit(f"Erreur génération thème: {str(e)}")
    
    @pyqtSlot(str, result=bool)
    def setPersonaDomain(self, domain):
        """Sélectionne un domaine de personas"""
        if domain in get_available_domains():
            self.current_domain = domain
            return True
        return False
    
    @pyqtSlot(str, str, str, bool, str)
    def startDebate(self, topic, prompt_one="", prompt_two="", use_moderator=True, domain=""):
        """Démarre le débat avec personas optionnelles"""
        if self.is_running:
            return
        
        # Utilisation des personas si domaine spécifié
        if domain and domain in get_available_domains():
            persona_opt = get_persona(domain, "optimiste")
            persona_skep = get_persona(domain, "sceptique")
            
            if persona_opt and persona_skep:
                prompt_one = persona_opt["prompt"]
                prompt_two = persona_skep["prompt"]
                
                # Utilise le topic associé au domaine
                domain_topic = get_topic_for_domain(domain)
                if domain_topic:
                    topic = domain_topic["question"]
        
        # Fallbacks avec prompts système 2025
        if not topic:
            topic = "Devons-nous faire confiance à l'IA en 2025?"
        if not prompt_one:
            prompt_one = self.agent_one.get_system_prompt()
        if not prompt_two:
            prompt_two = self.agent_two.get_system_prompt()
        
        # Créer worker avec fact-checker
        self.worker = AgentWorkerModern(
            self.agent_one, self.agent_two, self.moderator, self.fact_checker,
            topic, prompt_one, prompt_two, use_moderator
        )
        
        # Connexions signaux
        self.worker.messageStream.connect(self.messageStreamReceived)
        self.worker.messageComplete.connect(self.messageCompleted)
        self.worker.searchNotification.connect(self.searchStarted)
        self.worker.factCheckResult.connect(self.factCheckUpdate)
        self.worker.errorOccurred.connect(self.errorOccurred)
        self.worker.finished.connect(self.onDebateFinished)
        
        # Démarrage
        self.worker.start()
        self.is_running = True
        self.debateStatusChanged.emit(True)
    
    @pyqtSlot()
    def stopDebate(self):
        """Arrête le débat"""
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait()
            self.is_running = False
            self.debateStatusChanged.emit(False)
    
    def onDebateFinished(self):
        """Débat terminé"""
        self.is_running = False
        self.debateStatusChanged.emit(False)
        self.debateFinished.emit()
    
    # Méthodes compatibilité
    @pyqtSlot(result=str)
    def getDefaultTopic(self):
        return "Devons-nous faire confiance à l'IA pour les diagnostics médicaux?"
    
    @pyqtSlot(result=str)
    def getDefaultUserTopic(self):
        return "Intelligence artificielle et société"
    
    @pyqtSlot(result=str)
    def getOptimisticPrompt(self):
        return "Tu es un fervent optimiste technologique..."
    
    @pyqtSlot(result=str)
    def getCautiousPrompt(self):
        return "Tu es un sceptique technologique féroce..."
    
    @pyqtSlot(result=list)
    def getAvailablePersonas(self):
        """Liste des domaines de personas disponibles"""
        return get_available_domains()