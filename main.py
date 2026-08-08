#!/usr/bin/env python3
"""
AI Show V.TV — point d'entrée : interface QML + moteur show (`src/show/`).
"""

import os
import sys
from pathlib import Path

from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtQml import QQmlApplicationEngine

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from backend_bridge import ShowBridge


def main():
    os.environ.setdefault("QT_QUICK_CONTROLS_STYLE", "Basic")

    app = QGuiApplication(sys.argv)
    app.setApplicationName("AI Show V.TV")
    app.setOrganizationName("AI Debate Systems")

    engine = QQmlApplicationEngine()
    backend = ShowBridge()
    engine.rootContext().setContextProperty("backend", backend)

    qml_file = Path(__file__).resolve().parent / "src" / "ui" / "qml" / "ModernDebateInterface.qml"
    if not qml_file.exists():
        print(f"Erreur: {qml_file} non trouvé")
        sys.exit(1)

    engine.load(QUrl.fromLocalFile(str(qml_file)))
    if not engine.rootObjects():
        print("Erreur: Impossible de charger l'interface QML")
        sys.exit(1)

    print("AI Show V.TV — lancement (fermez la fenêtre pour quitter)")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
