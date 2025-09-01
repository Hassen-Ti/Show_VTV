#!/usr/bin/env python3
"""
AI Show V.TV - Interface QML Moderne
Point d'entrée principal avec nouvelle architecture
"""

import sys
import os
from pathlib import Path
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtQml import QQmlApplicationEngine
from PyQt6.QtCore import QUrl

# Ajouter src au path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from backend_bridge import BackendBridgeModern

def main():
    # Configuration Qt
    os.environ["QT_QUICK_CONTROLS_STYLE"] = "Basic"
    
    app = QGuiApplication(sys.argv)
    app.setApplicationName("AI Show V.TV")
    app.setOrganizationName("AI Debate Systems")
    
    # Engine QML
    engine = QQmlApplicationEngine()
    
    # Backend moderne
    backend = BackendBridgeModern()
    engine.rootContext().setContextProperty("backend", backend)
    
    # Chargement QML
    qml_file = Path(__file__).parent / "src" / "ui" / "qml" / "ModernDebateInterface.qml"
    
    if not qml_file.exists():
        print(f"Erreur: {qml_file} non trouvé")
        sys.exit(1)
    
    engine.load(QUrl.fromLocalFile(str(qml_file)))
    
    if not engine.rootObjects():
        print("Erreur: Impossible de charger l'interface QML")
        sys.exit(1)
    
    # Vérification assets
    assets_path = Path(__file__).parent / "src" / "ui" / "assets"
    required_assets = [
        "versus.png", "avatar_blue.gif", "avatar_red.gif",
        "avatar_blue_static.png", "avatar_red_static.png"
    ]
    
    missing = [asset for asset in required_assets if not (assets_path / asset).exists()]
    if missing:
        print(f"Attention: Assets manquants: {missing}")
        print("L'application fonctionnera mais sans certains visuels.")
    
    print("=" * 60)
    print("🎬 AI SHOW V.TV - DÉBATS DU FUTUR 🎬")
    print("=" * 60)
    print("NOUVELLES FONCTIONNALITÉS:")
    print("✅ 3 Personas pré-définies (Politique, Économie, Santé)")
    print("✅ 5 Topics dans un monde d'IA futuriste")
    print("✅ Historique complet pour tous les agents")
    print("✅ Fact-checker en temps réel")
    print("✅ Délais optimisés pour lecture")
    print("✅ Architecture moderne avec src/ layout")
    print("=" * 60)
    print("Monde futuriste où les IA sont citoyennes...")
    print("Débats télévisés entre IA sur l'avenir de l'humanité!")
    print("=" * 60)
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()