#!/usr/bin/env python3
"""
QML-based Multi-Tool Agent Interface
Modern UI using QML with Python backend
"""

import sys
import os
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtQml import QQmlApplicationEngine, qmlRegisterType
from PyQt6.QtCore import QUrl
from backend_bridge import BackendBridge


def main():
    # Set style before creating application
    os.environ["QT_QUICK_CONTROLS_STYLE"] = "Basic"
    
    # Create Qt application
    app = QGuiApplication(sys.argv)
    
    # Set application metadata
    app.setApplicationName("Multi-Tool Agent Debate")
    app.setOrganizationName("AI Debate Systems")
    
    # Create QML engine
    engine = QQmlApplicationEngine()
    
    # Create and register backend bridge
    backend = BackendBridge()
    engine.rootContext().setContextProperty("backend", backend)
    
    # Load QML file
    qml_file = os.path.join(os.path.dirname(__file__), "DebateInterface.qml")
    
    if not os.path.exists(qml_file):
        print(f"Error: QML file not found at {qml_file}")
        sys.exit(1)
    
    engine.load(QUrl.fromLocalFile(qml_file))
    
    # Check if QML loaded successfully
    if not engine.rootObjects():
        print("Error: Failed to load QML interface")
        sys.exit(1)
    
    # Check for required assets
    required_assets = [
        "versus.png",
        "avatar_blue.gif", 
        "avatar_red.gif",
        "avatar_blue_static.png",
        "avatar_red_static.png"
    ]
    
    missing_assets = []
    for asset in required_assets:
        if not os.path.exists(asset):
            missing_assets.append(asset)
    
    if missing_assets:
        print(f"Warning: Some assets are missing: {missing_assets}")
        print("The application will still run but may not display all visuals correctly.")
        print("Run 'python create_avatars.py' to generate avatar images.")
    
    print("=" * 50)
    print("Multi-Tool Agent QML Interface Started")
    print("=" * 50)
    print("Features:")
    print("- Modern QML-based UI with animations")
    print("- Real-time streaming responses")
    print("- Web search integration")
    print("- Customizable agent prompts")
    print("- Visual effects and particle animations")
    print("=" * 50)
    
    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()