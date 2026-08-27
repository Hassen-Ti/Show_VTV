"""
Pont Python ↔ QML : exécute le moteur show (LangGraph) et traduit les événements en signaux Qt.

Consomme le moteur uniquement via ``run_show`` + callbacks ``emit`` / oreillette.
Mapping UI des invités : ``guest_a`` → ``agent_one``, ``guest_b`` → ``agent_two`` ;
le modérateur reste ``moderator``.
"""

from __future__ import annotations

import os
import threading
import time
from typing import Any, Optional

from dotenv import load_dotenv
from openai import OpenAI
from PyQt6.QtCore import QObject, QThread, pyqtSignal, pyqtSlot

from config.show_config import SHOW_CONFIG
from config.show_presets import PRESET_KEYS, build_guests, get_preset, guest_names
from show import llm
from show.graph.show_graph import run_show

_AGENT_UI = {"guest_a": "agent_one", "guest_b": "agent_two"}
_STREAM_DELAY = 0.03
_MAX_EARPIECE_QUEUE = 3


class ShowStopped(Exception):
    """Le worker a demandé l'arrêt du show en cours."""


class ShowWorker(QThread):
    messageStream = pyqtSignal(str, str, int)
    messageComplete = pyqtSignal(str, str, int)
    searchStarted = pyqtSignal(str, str)
    backstageUpdate = pyqtSignal(str)
    # Question spectateur acceptée dans la file oreillette (avant lecture antenne).
    audienceQuestionQueued = pyqtSignal(str)
    # Oreillette drainée par le modérateur — question présentée / en cours de lecture.
    audienceQuestionRead = pyqtSignal(str)
    errorOccurred = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(
        self,
        topic: str,
        preset_key: str,
        client: OpenAI,
        *,
        initial_earpiece_queue: Optional[list[str]] = None,
    ):
        super().__init__()
        self.topic = topic
        self.preset_key = preset_key
        self.client = client
        self.should_stop = False
        self._earpiece_lock = threading.Lock()
        self._earpiece_queue: list[str] = []
        for raw in initial_earpiece_queue or []:
            cleaned = raw.strip()
            if cleaned and len(self._earpiece_queue) < _MAX_EARPIECE_QUEUE:
                self._earpiece_queue.append(cleaned)

    def submit_earpiece(self, text: str, *, announce: bool = True) -> bool:
        """Ajoute une question spectateur (max 3 en file). Renvoie False si file pleine.

        ``announce=False`` : enqueue silencieux (items déjà annoncés via le bridge
        pendant le pré-show) pour éviter un double ``audienceQuestionQueued``.
        """
        cleaned = text.strip()
        if not cleaned:
            return False
        with self._earpiece_lock:
            if len(self._earpiece_queue) >= _MAX_EARPIECE_QUEUE:
                return False
            self._earpiece_queue.append(cleaned)
        if announce:
            self.audienceQuestionQueued.emit(cleaned)
        return True

    def earpiece_depth(self) -> int:
        with self._earpiece_lock:
            return len(self._earpiece_queue)

    def _peek_earpiece(self) -> bool:
        with self._earpiece_lock:
            return len(self._earpiece_queue) > 0

    def _poll_earpiece(self) -> Optional[str]:
        with self._earpiece_lock:
            if self._earpiece_queue:
                return self._earpiece_queue.pop(0)
            return None

    def stop(self) -> None:
        self.should_stop = True

    def _check_stop(self) -> None:
        if self.should_stop:
            raise ShowStopped()

    def _ui_agent(self, agent_id: str) -> str:
        return _AGENT_UI.get(agent_id, agent_id)

    def _stream_message(self, ui_agent: str, text: str, round_num: int) -> None:
        words = text.split()
        for i, word in enumerate(words):
            self._check_stop()
            chunk = word + (" " if i < len(words) - 1 else "")
            self.messageStream.emit(ui_agent, chunk, round_num)
            time.sleep(_STREAM_DELAY)
        self.messageComplete.emit(ui_agent, text, round_num)

    def _handle_event(self, event: dict[str, Any]) -> None:
        self._check_stop()
        kind = event["type"]

        if kind == "moderator":
            self._stream_message("moderator", event["text"], int(event.get("round", 0)))
            return

        if kind == "turn":
            ui_agent = self._ui_agent(event["agent"])
            self._stream_message(ui_agent, event["text"], int(event.get("round", 0)))
            return

        if kind == "step":
            ui_agent = self._ui_agent(event["agent"])
            label = event.get("label", event.get("step", ""))
            self.searchStarted.emit(ui_agent, label)
            return

        if kind == "inner_monologue":
            ui_agent = self._ui_agent(event["agent"])
            self.backstageUpdate.emit(f"💭 {ui_agent} — {event['text']}")
            return

        if kind == "earpiece":
            # Moteur a drainé la file → lecture antenne (distinct de Queued).
            self.audienceQuestionRead.emit(event["text"])
            return

        if kind == "stance_update":
            tension = event.get("tension", 0.0)
            stances = event.get("stances", {})
            parts = [f"{aid}: {v:+.2f}" for aid, v in stances.items()]
            self.backstageUpdate.emit(
                f"📊 Tension {tension:.2f} | positions {', '.join(parts)}"
            )

    def run(self) -> None:
        try:
            guest_a, guest_b = build_guests(self.preset_key)

            def emit(event: dict[str, Any]) -> None:
                self._handle_event(event)

            run_show(
                self.topic,
                guest_a,
                guest_b,
                max_rounds=int(SHOW_CONFIG["max_rounds"]),
                client=self.client,
                enable_web_search=bool(SHOW_CONFIG.get("enable_web_search", True)),
                emit=emit,
                poll_earpiece=self._poll_earpiece,
                peek_earpiece=self._peek_earpiece,
            )
            self.finished.emit()
        except ShowStopped:
            self.finished.emit()
        except Exception as e:
            self.errorOccurred.emit(str(e))
            self.finished.emit()


class ThemeGenerationWorker(QThread):
    themeReady = pyqtSignal(str)
    failed = pyqtSignal(str)

    def __init__(self, user_topic: str):
        super().__init__()
        self._topic = user_topic

    def run(self) -> None:
        try:
            theme = llm.think(
                SHOW_CONFIG["model_internal"],
                "Tu es un animateur de débat télévisé professionnel.",
                (
                    f'Thème général : "{self._topic}"\n\n'
                    "Génère UNE question de débat spécifique, controversée et actuelle. "
                    "Réponds uniquement avec la question, sans introduction."
                ),
                temperature=0.8,
                max_tokens=120,
            )
            self.themeReady.emit(theme.strip())
        except Exception as e:
            self.failed.emit(str(e))


class ShowBridge(QObject):
    """Backend exposé à QML."""

    messageStreamReceived = pyqtSignal(str, str, int)
    messageCompleted = pyqtSignal(str, str, int)
    searchStarted = pyqtSignal(str, str)
    backstageUpdate = pyqtSignal(str)
    # Miroir worker : question acceptée en file (pré-show ou live). Capacité max 3.
    audienceQuestionQueued = pyqtSignal(str)
    # Miroir worker : question drainée / lue à l'antenne par le modérateur.
    audienceQuestionRead = pyqtSignal(str)
    errorOccurred = pyqtSignal(str)
    debateFinished = pyqtSignal()
    debateStatusChanged = pyqtSignal(bool)
    themeGenerated = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY manquant — copiez .env.example vers .env")
        self._client = OpenAI(api_key=api_key)
        self._worker: Optional[ShowWorker] = None
        self._theme_worker: Optional[ThemeGenerationWorker] = None
        self.is_running = False
        self._pending_earpiece_lock = threading.Lock()
        self._pending_earpiece_queue: list[str] = []

    def _live_worker(self) -> Optional[ShowWorker]:
        """Worker actif réellement en cours (évite de pousser vers un thread mort)."""
        worker = self._worker
        if worker is not None and worker.isRunning():
            return worker
        return None

    def _pending_depth(self) -> int:
        with self._pending_earpiece_lock:
            return len(self._pending_earpiece_queue)

    @pyqtSlot(str)
    def generateTheme(self, user_topic: str) -> None:
        self._theme_worker = ThemeGenerationWorker(user_topic)
        self._theme_worker.themeReady.connect(self.themeGenerated.emit)
        self._theme_worker.failed.connect(
            lambda err: self.errorOccurred.emit(f"Erreur génération thème : {err}")
        )
        self._theme_worker.start()

    @pyqtSlot(str, result=bool)
    def submitAudienceQuestion(self, text: str) -> bool:
        """Question du public → oreillette du modérateur (avant ou pendant le direct).

        Capacité partagée : max ``_MAX_EARPIECE_QUEUE`` (3) en file pending *ou* live.
        """
        cleaned = text.strip()
        if not cleaned:
            return False

        worker = self._live_worker()
        if self.is_running and worker is not None:
            return worker.submit_earpiece(cleaned)

        # Hors antenne, ou worker encore en arrêt : file pré-show.
        with self._pending_earpiece_lock:
            if len(self._pending_earpiece_queue) >= _MAX_EARPIECE_QUEUE:
                return False
            self._pending_earpiece_queue.append(cleaned)
        self.audienceQuestionQueued.emit(cleaned)
        return True

    @pyqtSlot(result=int)
    def getEarpieceQueueDepth(self) -> int:
        """Nombre de questions encore en file (pré-show ou worker live)."""
        worker = self._live_worker()
        if self.is_running and worker is not None:
            return worker.earpiece_depth()
        return self._pending_depth()

    @pyqtSlot(result=int)
    def getEarpieceQueueCapacity(self) -> int:
        return _MAX_EARPIECE_QUEUE

    @pyqtSlot(str, str)
    def startDebate(self, topic: str, preset_key: str = "") -> None:
        if self.is_running:
            return
        # Un arrêt coopératif peut laisser le thread LLM vivant quelques secondes :
        # ne pas démarrer un second show en parallèle.
        if self._worker is not None and self._worker.isRunning():
            self.errorOccurred.emit(
                "Un show est encore en cours d'arrêt — réessayez dans un instant."
            )
            return

        preset = get_preset(preset_key or "")
        final_topic = topic.strip() or preset.topic
        with self._pending_earpiece_lock:
            pending = list(self._pending_earpiece_queue)
            self._pending_earpiece_queue.clear()

        self._worker = ShowWorker(
            final_topic,
            preset_key or "",
            self._client,
            initial_earpiece_queue=pending,
        )
        self._worker.messageStream.connect(self.messageStreamReceived)
        self._worker.messageComplete.connect(self.messageCompleted)
        self._worker.searchStarted.connect(self.searchStarted)
        self._worker.backstageUpdate.connect(self.backstageUpdate)
        self._worker.audienceQuestionQueued.connect(self.audienceQuestionQueued)
        self._worker.audienceQuestionRead.connect(self.audienceQuestionRead)
        self._worker.errorOccurred.connect(self.errorOccurred)
        self._worker.finished.connect(self._on_debate_finished)

        # Marquer running *avant* start() pour que submitAudienceQuestion
        # route vers le worker pendant le démarrage du thread.
        self.is_running = True
        self.debateStatusChanged.emit(True)
        self._worker.start()

    @pyqtSlot()
    def stopDebate(self) -> None:
        if self._worker and self._worker.isRunning():
            self._worker.stop()
            finished = self._worker.wait(15000)
            if not finished and self.is_running:
                # LLM in-flight can outlive the cooperative stop; unlock UI so restart works.
                self.is_running = False
                self.debateStatusChanged.emit(False)
                self.errorOccurred.emit(
                    "Arrêt demandé — le tour en cours peut encore finir en arrière-plan."
                )

    def _on_debate_finished(self) -> None:
        if self.is_running:
            self.is_running = False
            self.debateStatusChanged.emit(False)
        self.debateFinished.emit()

    @pyqtSlot(result=str)
    def getDefaultTopic(self) -> str:
        return get_preset("").topic

    @pyqtSlot(result=str)
    def getDefaultUserTopic(self) -> str:
        return get_preset("").theme_hint

    @pyqtSlot(str, result="QVariantMap")
    def getGuestNames(self, preset_key: str) -> dict:
        return guest_names(preset_key or "")

    @pyqtSlot(result=list)
    def getPresetKeys(self) -> list:
        return PRESET_KEYS
