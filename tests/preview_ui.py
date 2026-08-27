"""
Aperçu visuel de l'interface QML sans backend réel.

Charge ModernDebateInterface.qml avec un backend factice, simule un débat en
cours, puis capture des screenshots (état repos + état en direct).

Usage: uv run python tests/preview_ui.py
"""

import sys
from pathlib import Path

from PyQt6.QtCore import QObject, QTimer, QUrl, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtQml import QQmlApplicationEngine
from PyQt6.QtQuick import QQuickWindow  # noqa: F401

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "docs" / "screenshots"
_MAX_EARPIECE = 3


class MockBackend(QObject):
    messageStreamReceived = pyqtSignal(str, str, int)
    messageCompleted = pyqtSignal(str, str, int)
    searchStarted = pyqtSignal(str, str)
    backstageUpdate = pyqtSignal(str)
    # Aligné bridge : Queued = en file ; Read = drainée / lue à l'antenne.
    audienceQuestionQueued = pyqtSignal(str)
    audienceQuestionRead = pyqtSignal(str)
    errorOccurred = pyqtSignal(str)
    debateFinished = pyqtSignal()
    debateStatusChanged = pyqtSignal(bool)
    themeGenerated = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._earpiece: list[str] = []
        self._running = False

    @pyqtSlot(result=str)
    def getDefaultTopic(self):
        return "Devons-nous faire confiance à l'IA pour les diagnostics médicaux?"

    @pyqtSlot(result=str)
    def getDefaultUserTopic(self):
        return "Intelligence artificielle et société"

    @pyqtSlot(str, result="QVariantMap")
    def getGuestNames(self, preset_key: str):
        return {"left": "Provocateur Physicien", "right": "Diplomate Philosophe"}

    @pyqtSlot(result=int)
    def getEarpieceQueueDepth(self):
        return len(self._earpiece)

    @pyqtSlot(result=int)
    def getEarpieceQueueCapacity(self):
        return _MAX_EARPIECE

    @pyqtSlot(str)
    def generateTheme(self, user_topic):
        self.themeGenerated.emit("L'IA médicale doit-elle avoir le dernier mot?")

    @pyqtSlot(str, str)
    def startDebate(self, topic, preset_key=""):
        self._running = True
        self.debateStatusChanged.emit(True)

    @pyqtSlot(str, result=bool)
    def submitAudienceQuestion(self, text):
        cleaned = text.strip()
        if not cleaned:
            return False
        if len(self._earpiece) >= _MAX_EARPIECE:
            return False
        self._earpiece.append(cleaned)
        self.audienceQuestionQueued.emit(cleaned)
        return True

    @pyqtSlot()
    def stopDebate(self):
        self._running = False
        self._earpiece.clear()
        self.debateStatusChanged.emit(False)

    def drain_one(self):
        """Helper preview : simule une lecture antenne (audienceQuestionRead)."""
        if not self._earpiece:
            return
        text = self._earpiece.pop(0)
        self.audienceQuestionRead.emit(text)


def simulate_live(backend: MockBackend):
    backend.debateStatusChanged.emit(True)
    backend.submitAudienceQuestion("Et si l'IA se trompe sur les peaux foncées ?")
    backend.messageStreamReceived.emit(
        "moderator",
        "Bonsoir et bienvenue sur le plateau de Show V.TV ! Avant de commencer, "
        "un téléspectateur nous écrit : et si l'IA se trompait sur les peaux foncées ? "
        "Ce soir, un débat qui fâche : faut-il confier nos diagnostics médicaux à une machine ?",
        0,
    )
    backend.drain_one()
    backend.messageStreamReceived.emit(
        "agent_one",
        "Les chiffres sont têtus : sur la détection précoce de certains cancers, "
        "les modèles d'imagerie dépassent déjà les radiologues seuls.",
        1,
    )
    backend.messageStreamReceived.emit(
        "agent_two",
        "Un copilote infaillible, rien que ça ! Ces mêmes modèles se trompent "
        "silencieusement dès que le patient sort de la distribution d'entraînement.",
        1,
    )
    backend.searchStarted.emit("agent_one", "vérifie les faits")
    backend.backstageUpdate.emit(
        "💭 agent_one — Je doute plus que je ne le montre. Mais je tiens ma ligne."
    )
    backend.backstageUpdate.emit("📊 Tension 0.62 | positions guest_a: +0.78, guest_b: -0.55")


def main():
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()
    backend = MockBackend()
    engine.rootContext().setContextProperty("backend", backend)

    qml_file = ROOT / "src" / "ui" / "qml" / "ModernDebateInterface.qml"
    engine.load(QUrl.fromLocalFile(str(qml_file)))
    if not engine.rootObjects():
        print("Echec du chargement QML")
        sys.exit(1)

    window = engine.rootObjects()[0]
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    def grab(name):
        image = window.grabWindow()
        path = OUT_DIR / name
        image.save(str(path))
        print(f"Screenshot: {path}", flush=True)

    QTimer.singleShot(800, lambda: grab("ui_preview_idle.png"))
    QTimer.singleShot(1200, lambda: simulate_live(backend))
    QTimer.singleShot(2000, lambda: grab("ui_preview_live.png"))
    QTimer.singleShot(2400, app.quit)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
