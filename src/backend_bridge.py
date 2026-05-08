"""
Pont Python ↔ QML : débat avec historique, délais et fact-checking.
"""

import time

from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, QThread

from agents.agent_1 import Agent_one
from agents.agent_2 import Agent_two
from agents.agent_moderator import AgentModerator
from agents.agent_factchecker import AgentFactChecker
from config.settings import DEBATE_CONFIG
from config.personas import get_persona, get_available_domains
from config.topics import get_topic_for_domain
from utils.token_manager import token_manager

_AGENT_LABEL = {"agent_one": "Agent One", "agent_two": "Agent Two"}


class AgentWorkerModern(QThread):
    """Worker : boucle de débat avec historique et fact-checking."""

    messageStream = pyqtSignal(str, str, int)
    messageComplete = pyqtSignal(str, str, int)
    searchNotification = pyqtSignal(str, str)
    factCheckResult = pyqtSignal(str, str)
    errorOccurred = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(
        self,
        agent_one,
        agent_two,
        moderator,
        fact_checker,
        topic,
        prompt_one,
        prompt_two,
        use_moderator=True,
    ):
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
        self.debate_history = []

    def stop(self):
        self.should_stop = True

    def add_to_history(self, round_num, agent_type, message, message_type="response"):
        self.debate_history.append(
            {
                "round": round_num,
                "agent": agent_type,
                "message": message,
                "type": message_type,
                "timestamp": time.time(),
            }
        )

    def format_history_for_agent(self, current_agent):
        if not self.debate_history:
            return ""

        lines = ["🎬 HISTORIQUE DU DÉBAT (pour référence):\n"]
        for entry in self.debate_history[-8:]:
            agent_name = {
                "moderator": "🎙️ ANIMATEUR",
                "agent_one": "🔥 ADVERSAIRE" if current_agent == "agent_two" else "🔥 VOUS",
                "agent_two": "💀 ADVERSAIRE" if current_agent == "agent_one" else "💀 VOUS",
            }.get(entry["agent"], entry["agent"])
            lines.append(f"[Round {entry['round']}] {agent_name}: {entry['message']}\n")

        lines.append("\n🎯 RÉPONDEZ MAINTENANT en tenant compte de cet historique!")
        return "".join(lines)

    def stream_moderator_message(self, message, round_num=0):
        """Effet « frappe » avec un signal par mot (moins de charge que caractère par caractère)."""
        words = message.split()
        for i, word in enumerate(words):
            if self.should_stop:
                break
            chunk = word + (" " if i < len(words) - 1 else "")
            self.messageStream.emit("moderator", chunk, round_num)
            time.sleep(0.03)

        self.messageComplete.emit("moderator", message, round_num)
        self.add_to_history(round_num, "moderator", message, "moderation")

    def _run_agent_turn(self, agent, stream_key, user_input, display_round, fact_label):
        history_context = self.format_history_for_agent(stream_key)
        tokens = token_manager.get_current_tokens()
        full_prompt = f"{agent.get_system_prompt(tokens)}\n\n{history_context}"

        def stream_cb(chunk):
            self.messageStream.emit(stream_key, chunk, display_round)

        def search_cb(info):
            self.searchNotification.emit(stream_key, info)

        response = agent.generate_streaming_response_with_search(
            user_input,
            full_prompt,
            stream_callback=stream_cb,
            search_callback=search_cb,
        )

        if response.startswith("Error:"):
            self.errorOccurred.emit(f"{_AGENT_LABEL[stream_key]}: {response}")
            return None

        self.messageComplete.emit(stream_key, response, display_round)
        self.add_to_history(display_round, stream_key, response)

        if self.fact_checker:
            fact_result = self.fact_checker.quick_fact_check(response, fact_label)
            self.factCheckResult.emit(stream_key, fact_result)

        time.sleep(DEBATE_CONFIG["response_delay_seconds"])
        return response

    def run(self):
        try:
            if self.use_moderator:
                intro = self.moderator.introduce_debate(self.topic)
                self.stream_moderator_message(intro, 0)
                if self.should_stop:
                    return
                time.sleep(DEBATE_CONFIG["moderator_delay_seconds"])

            for round_num in range(DEBATE_CONFIG["max_rounds"]):
                if self.should_stop:
                    break
                display_round = round_num + 1

                if self.use_moderator:
                    floor_msg = self.moderator.give_floor_to_agent(
                        "Agent One 🔥",
                        is_first=(round_num == 0),
                        previous_argument=self.debate_history[-1]["message"]
                        if self.debate_history
                        else None,
                    )
                    self.stream_moderator_message(floor_msg, display_round)
                    if self.should_stop:
                        break
                    time.sleep(1)

                user_one = (
                    self.topic
                    if round_num == 0
                    else "Continuez le débat en répondant aux arguments précédents"
                )
                response_one = self._run_agent_turn(
                    self.agent_one,
                    "agent_one",
                    user_one,
                    display_round,
                    "Agent 1 🔥",
                )
                if response_one is None:
                    return
                if self.should_stop:
                    break

                if self.use_moderator:
                    floor_msg = self.moderator.give_floor_to_agent(
                        "Agent Two 💀",
                        is_first=False,
                        previous_argument=response_one,
                    )
                    self.stream_moderator_message(floor_msg, display_round)
                    if self.should_stop:
                        break
                    time.sleep(1)

                response_two = self._run_agent_turn(
                    self.agent_two,
                    "agent_two",
                    response_one,
                    display_round,
                    "Agent 2 💀",
                )
                if response_two is None:
                    return

                if (
                    self.use_moderator
                    and display_round % 2 == 0
                    and round_num < DEBATE_CONFIG["max_rounds"] - 1
                ):
                    if self.should_stop:
                        break
                    interjection = self.moderator.interject_or_summarize(
                        response_one, response_two, display_round
                    )
                    self.stream_moderator_message(interjection, display_round)
                    time.sleep(DEBATE_CONFIG["moderator_delay_seconds"])

            if self.use_moderator and not self.should_stop:
                conclusion = self.moderator.conclude_debate(
                    f"Débat passionnant sur: {self.topic}"
                )
                self.stream_moderator_message(conclusion, DEBATE_CONFIG["max_rounds"] + 1)

            self.finished.emit()

        except Exception as e:
            self.errorOccurred.emit(f"Erreur worker: {str(e)}")


class ThemeGenerationWorker(QThread):
    themeReady = pyqtSignal(str)
    failed = pyqtSignal(str)

    def __init__(self, moderator, user_topic: str):
        super().__init__()
        self._moderator = moderator
        self._topic = user_topic

    def run(self):
        try:
            theme = self._moderator.generate_debate_theme(self._topic)
            self.themeReady.emit(theme)
        except Exception as e:
            self.failed.emit(str(e))


class BackendBridgeModern(QObject):
    """Backend exposé à QML."""

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
        try:
            self.agent_one = Agent_one()
            self.agent_two = Agent_two()
            self.moderator = AgentModerator()
            self.fact_checker = AgentFactChecker()
        except ValueError as e:
            print(f"Erreur initialisation agents: {e}")
            raise

        self.worker = None
        self._theme_worker = None
        self.is_running = False
        self.current_domain = None

    @pyqtSlot(str)
    def generateTheme(self, user_topic):
        self._theme_worker = ThemeGenerationWorker(self.moderator, user_topic)
        self._theme_worker.themeReady.connect(self.themeGenerated.emit)
        self._theme_worker.failed.connect(
            lambda err: self.errorOccurred.emit(f"Erreur génération thème: {err}")
        )
        self._theme_worker.start()

    @pyqtSlot(str, result=bool)
    def setPersonaDomain(self, domain):
        if domain in get_available_domains():
            self.current_domain = domain
            return True
        return False

    @pyqtSlot(str, str, str, bool, str)
    def startDebate(self, topic, prompt_one="", prompt_two="", use_moderator=True, domain=""):
        if self.is_running:
            return

        if domain and domain in get_available_domains():
            persona_opt = get_persona(domain, "optimiste")
            persona_skep = get_persona(domain, "sceptique")
            if persona_opt and persona_skep:
                prompt_one = persona_opt["prompt"]
                prompt_two = persona_skep["prompt"]
                domain_topic = get_topic_for_domain(domain)
                if domain_topic:
                    topic = domain_topic["question"]

        if not topic:
            topic = "Devons-nous faire confiance à l'IA en 2025?"
        if not prompt_one:
            prompt_one = self.agent_one.get_system_prompt()
        if not prompt_two:
            prompt_two = self.agent_two.get_system_prompt()

        self.worker = AgentWorkerModern(
            self.agent_one,
            self.agent_two,
            self.moderator,
            self.fact_checker,
            topic,
            prompt_one,
            prompt_two,
            use_moderator,
        )

        self.worker.messageStream.connect(self.messageStreamReceived)
        self.worker.messageComplete.connect(self.messageCompleted)
        self.worker.searchNotification.connect(self.searchStarted)
        self.worker.factCheckResult.connect(self.factCheckUpdate)
        self.worker.errorOccurred.connect(self.errorOccurred)
        self.worker.finished.connect(self.onDebateFinished)

        self.worker.start()
        self.is_running = True
        self.debateStatusChanged.emit(True)

    @pyqtSlot()
    def stopDebate(self):
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait(5000)
            self.is_running = False
            self.debateStatusChanged.emit(False)

    def onDebateFinished(self):
        self.is_running = False
        self.debateStatusChanged.emit(False)
        self.debateFinished.emit()

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
        return get_available_domains()
