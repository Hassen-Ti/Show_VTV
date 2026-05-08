#!/usr/bin/env python3
"""
AI Show V.TV — point d'entrée : interface QML + pont Python (`src/`).
"""

import sys
import os
from pathlib import Path
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtQml import QQmlApplicationEngine
from PyQt6.QtCore import QUrl

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from backend_bridge import BackendBridgeModern


def main():
    os.environ["QT_QUICK_CONTROLS_STYLE"] = "Basic"

    app = QGuiApplication(sys.argv)
    app.setApplicationName("AI Show V.TV")
    app.setOrganizationName("AI Debate Systems")

    engine = QQmlApplicationEngine()
    backend = BackendBridgeModern()
    engine.rootContext().setContextProperty("backend", backend)

    qml_file = Path(__file__).resolve().parent / "src" / "ui" / "qml" / "ModernDebateInterface.qml"
    if not qml_file.exists():
        print(f"Erreur: {qml_file} non trouvé")
        sys.exit(1)

    engine.load(QUrl.fromLocalFile(str(qml_file)))
    if not engine.rootObjects():
        print("Erreur: Impossible de charger l'interface QML")
        sys.exit(1)

    assets_path = Path(__file__).resolve().parent / "src" / "ui" / "assets"
    required_assets = [
        "versus.png",
        "avatar_blue.gif",
        "avatar_red.gif",
        "avatar_blue_static.png",
        "avatar_red_static.png",
    ]
    missing = [a for a in required_assets if not (assets_path / a).exists()]
    if missing:
        print(f"Attention: assets manquants: {missing}")

    print("AI Show V.TV — lancement (Ctrl+C dans le terminal ne suffit pas : fermer la fenêtre)")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
