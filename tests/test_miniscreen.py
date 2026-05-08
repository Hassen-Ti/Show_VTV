#!/usr/bin/env python3
"""
Demo visuelle avec VRAIES captures d'ecran
Utilise l'API Microlink pour afficher les vraies miniatures
"""

import sys
from pathlib import Path
import requests
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtQml import QQmlApplicationEngine
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, QTimer, QThread, QUrl

class ScreenshotWorker(QThread):
    """Thread pour capturer screenshots sans bloquer l'UI"""
    screenshotReady = pyqtSignal(str, str, str, str)  # position, title, url, screenshot_url
    screenshotError = pyqtSignal(str, str)  # position, error
    
    def __init__(self, position, title, url):
        super().__init__()
        self.position = position
        self.title = title
        self.url = url
    
    def run(self):
        """Capture le screenshot via API"""
        try:
            api_url = "https://api.microlink.io/screenshot"
            params = {
                'url': self.url,
                'type': 'png',
                'viewport.width': 400,
                'viewport.height': 250,
                'element': 'body'
            }
            
            response = requests.get(api_url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    screenshot_url = data['data']['screenshot']['url']
                    actual_title = data['data'].get('title', self.title)
                    self.screenshotReady.emit(
                        self.position, 
                        actual_title, 
                        self.url, 
                        screenshot_url
                    )
                    return
            
            self.screenshotError.emit(self.position, f"API Error: {response.status_code}")
            
        except Exception as e:
            self.screenshotError.emit(self.position, str(e))

class DemoController(QObject):
    """Controller avec vraies captures d'ecran"""
    
    showMiniScreen = pyqtSignal(str, str, str, str)  # position, title, url, screenshot_url
    hideMiniScreen = pyqtSignal(str)  # position
    updateAgentText = pyqtSignal(str, str)  # agent, text
    showLoadingScreen = pyqtSignal(str, str, str)  # position, title, url (sans screenshot)
    
    def __init__(self):
        super().__init__()
        self.demo_timer = QTimer()
        self.demo_step = 0
        self.demo_timer.timeout.connect(self.run_demo_step)
        self.workers = []  # Garde reference aux threads
    
    @pyqtSlot()
    def startDemo(self):
        """Lance la demo avec vraies captures"""
        self.demo_step = 0
        self.demo_timer.start(4000)  # 4 secondes entre etapes (plus de temps pour screenshots)
        self.run_demo_step()
    
    def capture_screenshot(self, position, title, url):
        """Lance capture screenshot dans thread"""
        # Affiche d'abord loading
        self.showLoadingScreen.emit(position, f"{title} (Chargement...)", url)
        
        # Lance capture en background
        worker = ScreenshotWorker(position, title, url)
        worker.screenshotReady.connect(self.on_screenshot_ready)
        worker.screenshotError.connect(self.on_screenshot_error)
        worker.start()
        self.workers.append(worker)  # Garde reference
    
    def on_screenshot_ready(self, position, title, url, screenshot_url):
        """Screenshot pret"""
        self.showMiniScreen.emit(position, title, url, screenshot_url)
    
    def on_screenshot_error(self, position, error):
        """Erreur screenshot"""
        self.showMiniScreen.emit(position, f"Erreur: {error}", "", "")
    
    def run_demo_step(self):
        """Execute etapes demo avec screenshots"""
        if self.demo_step == 0:
            self.updateAgentText.emit("left", "L'IA revolutionne les diagnostics medicaux!")
            
        elif self.demo_step == 1:
            # Capture screenshot Nature
            self.updateAgentText.emit("left", "Recherche d'etudes recentes...")
            self.capture_screenshot(
                "left",
                "Nature Medical AI Research", 
                "https://www.nature.com"
            )
            
        elif self.demo_step == 2:
            self.updateAgentText.emit("left", "Nature montre 94% de precision!")
            
        elif self.demo_step == 3:
            self.hideMiniScreen.emit("left")
            self.updateAgentText.emit("left", "")
            
        elif self.demo_step == 4:
            self.updateAgentText.emit("right", "Attention aux biais algorithmiques!")
            
        elif self.demo_step == 5:
            # Capture screenshot WHO
            self.updateAgentText.emit("right", "Recherche des problemes...")
            self.capture_screenshot(
                "right",
                "WHO AI Healthcare Guidelines",
                "https://www.who.int"
            )
            
        elif self.demo_step == 6:
            self.updateAgentText.emit("right", "L'OMS alerte sur les discriminations!")
            
        elif self.demo_step == 7:
            self.hideMiniScreen.emit("right")
            self.updateAgentText.emit("right", "")
            
        elif self.demo_step == 8:
            self.demo_timer.stop()
            self.demo_step = -1
            return
            
        self.demo_step += 1

def main():
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()
    
    controller = DemoController()
    engine.rootContext().setContextProperty("demoController", controller)
    
    qml_file = Path(__file__).resolve().parent / "test_miniscreen.qml"
    engine.load(QUrl.fromLocalFile(str(qml_file)))
    
    if not engine.rootObjects():
        print(f"Erreur: {qml_file} non trouve")
        sys.exit(1)
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()