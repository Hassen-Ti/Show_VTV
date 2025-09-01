import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Layouts

ApplicationWindow {
    id: mainWindow
    visible: true
    width: 1400
    height: 900
    title: "AI Show V.TV - Débats du Futur"
    color: "#001122"

    // Properties
    property bool debateRunning: false
    property string agent1Name: "Agent One"
    property string agent2Name: "Agent Two"
    property bool customizationVisible: false
    property bool moderatorEnabled: true
    property bool factCheckVisible: true
    property int agent1Round: 0
    property int agent2Round: 0
    property int moderatorRound: 0
    property string generatedTheme: ""
    property string selectedDomain: ""

    // Background avec nouveau chemin
    Image {
        id: bgImage
        anchors.fill: parent
        source: "../assets/versus.png"
        fillMode: Image.PreserveAspectCrop
        opacity: 0.3
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 20
        spacing: 15

        // Header réduit pour laisser place au background
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 30
            color: "transparent"
        }

        // Section sélection de personas
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 80
            color: Qt.rgba(0, 0.067, 0.133, 0.7)
            border.color: "#ffcc00"
            border.width: 2
            radius: 10
            
            RowLayout {
                anchors.fill: parent
                anchors.margins: 15
                spacing: 15
                
                Label {
                    text: "🎭 Personas:"
                    color: "#ffcc00"
                    font.pixelSize: 16
                    font.bold: true
                    font.family: "Consolas"
                }
                
                ComboBox {
                    id: personaSelector
                    Layout.preferredWidth: 200
                    model: ["Débat Libre", "⚡ Économie & Emplois", "📚 Éducation IA", "⚕️ Santé & Diagnostic", "👁️ Surveillance IA", "🎨 Création Artistique"]
                    
                    background: Rectangle {
                        color: "#221100"
                        border.color: "#ffcc00"
                        border.width: 1
                        radius: 5
                    }
                    
                    contentItem: Text {
                        text: personaSelector.displayText
                        color: "#ffcc00"
                        font.family: "Consolas"
                        verticalAlignment: Text.AlignVCenter
                        leftPadding: 10
                    }
                    
                    onCurrentIndexChanged: {
                        var domains = ["", "economie_emplois", "education_ia", "sante_diagnostic", "surveillance_securite", "art_creation"]
                        selectedDomain = domains[currentIndex]
                        
                        if (currentIndex > 0) {
                            // Auto-générer le thème pour le domaine
                            var topics = [
                                "",
                                "L'IA doit-elle remplacer les emplois humains?",
                                "L'IA peut-elle remplacer les professeurs?",
                                "Faut-il faire confiance aux diagnostics IA?",
                                "La surveillance par IA est-elle acceptable?",
                                "L'art créé par IA a-t-il de la valeur?"
                            ]
                            themeInput.text = topics[currentIndex]
                        }
                    }
                }
                
                Label {
                    text: "📝 Thématique:"
                    color: "#ffcc00"
                    font.pixelSize: 16
                    font.bold: true
                    font.family: "Consolas"
                }
                
                TextField {
                    id: themeInput
                    Layout.fillWidth: true
                    text: backend ? backend.getDefaultUserTopic() : "Intelligence artificielle et société"
                    placeholderText: "Ex: Intelligence artificielle, Environnement, Société..."
                    color: "#ffcc00"
                    font.family: "Consolas"
                    
                    background: Rectangle {
                        color: "#001122"
                        border.color: "#ffcc00"
                        border.width: 1
                        radius: 5
                    }
                }
                
                Button {
                    text: "🎬 Générer"
                    font.pixelSize: 14
                    font.bold: true
                    font.family: "Consolas"
                    palette.buttonText: "#ffcc00"
                    
                    background: Rectangle {
                        color: parent.hovered ? "#443300" : "#221100"
                        border.color: "#ffcc00"
                        border.width: 2
                        radius: 8
                    }
                    
                    onClicked: {
                        backend.generateTheme(themeInput.text)
                    }
                }
            }
        }

        // Zone de débat principale
        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 20

            // Agent Gauche
            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.preferredWidth: 400
                color: "transparent"
                
                ColumnLayout {
                    anchors.fill: parent
                    spacing: 10

                    // Espace sans avatar (plus épuré)
                    Item {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 40  // Réduit l'espace
                    }

                    // Agent Label avec persona dynamique
                    Label {
                        id: leftLabel
                        Layout.fillWidth: true
                        text: getPersonaLabel("left")
                        color: "#00aaff"
                        font.pixelSize: 16
                        font.bold: true
                        font.family: "Consolas"
                        horizontalAlignment: Text.AlignHCenter
                        wrapMode: Text.Wrap
                        maximumLineCount: 2
                    }

                    // Search indicator
                    Label {
                        id: leftSearchLabel
                        Layout.fillWidth: true
                        text: ""
                        color: "#00aaff"
                        font.pixelSize: 12
                        font.italic: true
                        horizontalAlignment: Text.AlignHCenter
                        visible: text !== ""
                    }

                    // Zone messages
                    Rectangle {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        color: Qt.rgba(0, 0.067, 0.133, 0.85)
                        border.color: "#00aaff"
                        border.width: 2
                        radius: 10
                        
                        ScrollView {
                            anchors.fill: parent
                            anchors.margins: 10
                            
                            TextArea {
                                id: leftTextArea
                                readOnly: true
                                wrapMode: TextArea.Wrap
                                color: "#00aaff"
                                font.pixelSize: 14
                                font.family: "Consolas"
                                font.bold: true
                                selectByMouse: true
                                text: "Agent One - En attente du débat..."
                                
                                background: Rectangle {
                                    color: "transparent"
                                }
                            }
                        }
                    }
                }
            }

            // Zone centrale - Modérateur + Fact-Checker
            Rectangle {
                Layout.preferredWidth: 500
                Layout.fillHeight: true
                color: "transparent"
                
                ColumnLayout {
                    anchors.fill: parent
                    spacing: 10
                    
                    // Moderateur avatar
                    Item {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 100
                        
                        Rectangle {
                            anchors.centerIn: parent
                            width: 80
                            height: 80
                            radius: 40
                            color: Qt.rgba(1, 0.8, 0, 0.2)
                            border.color: "#ffcc00"
                            border.width: 3
                            
                            Text {
                                anchors.centerIn: parent
                                text: "🎙️"
                                font.pixelSize: 40
                            }
                            
                            RotationAnimation on rotation {
                                running: debateRunning && moderatorEnabled
                                loops: Animation.Infinite
                                from: 0
                                to: 360
                                duration: 10000
                            }
                        }
                    }
                    
                    // Label et contrôles modérateur
                    Label {
                        Layout.fillWidth: true
                        text: "📺 MR BULLSHIT"
                        color: "#ffcc00"
                        font.pixelSize: 16
                        font.bold: true
                        font.family: "Consolas"
                        horizontalAlignment: Text.AlignHCenter
                    }
                    
                    // Switches
                    RowLayout {
                        Layout.alignment: Qt.AlignHCenter
                        spacing: 20
                        
                        Switch {
                            id: moderatorSwitch
                            checked: true
                            text: checked ? "Animateur ON" : "OFF"
                            palette.text: "#ffcc00"
                            font.pixelSize: 12
                            
                            onCheckedChanged: {
                                moderatorEnabled = checked
                            }
                        }
                        
                        Switch {
                            id: factCheckSwitch
                            checked: true
                            text: checked ? "Fact-Check ON" : "OFF"
                            palette.text: "#ff8800"
                            font.pixelSize: 12
                            
                            onCheckedChanged: {
                                factCheckVisible = checked
                            }
                        }
                    }
                    
                    // Messages modérateur
                    Rectangle {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        color: Qt.rgba(0.8, 0.6, 0, 0.05)
                        border.color: "#ffcc00"
                        border.width: 2
                        radius: 10
                        
                        ScrollView {
                            anchors.fill: parent
                            anchors.margins: 10
                            
                            TextArea {
                                id: moderatorTextArea
                                readOnly: true
                                wrapMode: TextArea.Wrap
                                color: "#ffcc00"
                                font.pixelSize: 15
                                font.family: "Consolas"
                                font.bold: true
                                selectByMouse: true
                                text: moderatorEnabled ? "🎬 Prêt pour le direct..." : "Mode débat direct"
                                
                                background: Rectangle {
                                    color: "transparent"
                                }
                            }
                        }
                    }
                    
                    // NOUVEAU: Zone Fact-Checker
                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: factCheckVisible ? 120 : 0
                        visible: factCheckVisible
                        color: Qt.rgba(0.8, 0.4, 0, 0.1)
                        border.color: "#ff8800"
                        border.width: 1
                        radius: 8
                        
                        Behavior on Layout.preferredHeight {
                            NumberAnimation { duration: 300 }
                        }
                        
                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: 10
                            
                            Label {
                                text: "🔍 FACT-CHECKER"
                                color: "#ff8800"
                                font.bold: true
                                font.pixelSize: 12
                                Layout.alignment: Qt.AlignHCenter
                            }
                            
                            ScrollView {
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                
                                TextArea {
                                    id: factCheckArea
                                    readOnly: true
                                    wrapMode: TextArea.Wrap
                                    color: "#ff8800"
                                    font.pixelSize: 11
                                    font.family: "Consolas"
                                    selectByMouse: true
                                    text: "⏳ En attente de vérifications..."
                                    
                                    background: Rectangle {
                                        color: "transparent"
                                    }
                                }
                            }
                        }
                    }
                }
            }

            // Agent Droite
            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.preferredWidth: 400
                color: "transparent"
                
                ColumnLayout {
                    anchors.fill: parent
                    spacing: 10

                    // Espace sans avatar (plus épuré)
                    Item {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 40  // Réduit l'espace
                    }

                    // Agent Label avec persona
                    Label {
                        id: rightLabel
                        Layout.fillWidth: true
                        text: getPersonaLabel("right")
                        color: "#ff4444"
                        font.pixelSize: 16
                        font.bold: true
                        font.family: "Consolas"
                        horizontalAlignment: Text.AlignHCenter
                        wrapMode: Text.Wrap
                        maximumLineCount: 2
                    }

                    // Search indicator
                    Label {
                        id: rightSearchLabel
                        Layout.fillWidth: true
                        text: ""
                        color: "#ff4444"
                        font.pixelSize: 12
                        font.italic: true
                        horizontalAlignment: Text.AlignHCenter
                        visible: text !== ""
                    }

                    // Zone messages
                    Rectangle {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        color: Qt.rgba(0.133, 0.067, 0.067, 0.85)
                        border.color: "#ff4444"
                        border.width: 2
                        radius: 10
                        
                        ScrollView {
                            anchors.fill: parent
                            anchors.margins: 10
                            
                            TextArea {
                                id: rightTextArea
                                readOnly: true
                                wrapMode: TextArea.Wrap
                                color: "#ff4444"
                                font.pixelSize: 14
                                font.family: "Consolas"
                                font.bold: true
                                selectByMouse: true
                                text: "Agent Two - En attente du débat..."
                                
                                background: Rectangle {
                                    color: "transparent"
                                }
                            }
                        }
                    }
                }
            }
        }

        // Contrôles inférieurs
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 80
            color: Qt.rgba(0, 0.067, 0.133, 0.7)
            border.color: "#00ffff"
            border.width: 1
            radius: 10
            
            RowLayout {
                anchors.fill: parent
                anchors.margins: 15
                spacing: 20
                
                Label {
                    text: "Question:"
                    color: "#00ffff"
                    font.pixelSize: 14
                    font.bold: true
                    font.family: "Consolas"
                }
                
                TextField {
                    id: topicInput
                    Layout.fillWidth: true
                    text: generatedTheme || (backend ? backend.getDefaultTopic() : "Devons-nous faire confiance à l'IA?")
                    placeholderText: "Question de débat..."
                    color: "#00ffff"
                    font.pixelSize: 14
                    font.family: "Consolas"
                    
                    background: Rectangle {
                        color: "#001122"
                        border.color: "#00ffff"
                        border.width: 1
                        radius: 5
                    }
                }
                
                Button {
                    id: startBtn
                    text: debateRunning ? "⚡ EN DIRECT..." : "🚀 LANCER"
                    enabled: !debateRunning
                    font.pixelSize: 16
                    font.bold: true
                    font.family: "Consolas"
                    palette.buttonText: enabled ? "#00ff00" : "#444444"
                    
                    background: Rectangle {
                        color: parent.enabled ? (parent.hovered ? "#004400" : "#002200") : "#111111"
                        border.color: parent.enabled ? "#00ff00" : "#444444"
                        border.width: 2
                        radius: 8
                    }
                    
                    onClicked: {
                        // Reset
                        leftTextArea.text = "🔥 Préparation..."
                        rightTextArea.text = "💀 Préparation..."
                        moderatorTextArea.text = "🎬 Direct dans 3... 2... 1..."
                        factCheckArea.text = "🔍 Fact-checker activé..."
                        agent1Round = 0
                        agent2Round = 0
                        moderatorRound = 0
                        
                        var finalTopic = topicInput.text || generatedTheme || (backend ? backend.getDefaultTopic() : "Devons-nous faire confiance à l'IA?")
                        
                        // Lancement avec persona domain
                        backend.startDebate(
                            finalTopic,
                            "", // prompt_one (sera remplacé par persona)
                            "", // prompt_two (sera remplacé par persona)
                            moderatorEnabled,
                            selectedDomain
                        )
                    }
                }
                
                Button {
                    id: stopBtn
                    text: "🛑 STOP"
                    enabled: debateRunning
                    font.pixelSize: 16
                    font.bold: true
                    font.family: "Consolas"
                    palette.buttonText: enabled ? "#ff4444" : "#444444"
                    
                    background: Rectangle {
                        color: parent.enabled ? (parent.hovered ? "#884444" : "#442222") : "#111111"
                        border.color: parent.enabled ? "#ff4444" : "#444444"
                        border.width: 2
                        radius: 8
                    }
                    
                    onClicked: {
                        backend.stopDebate()
                    }
                }
            }
        }
    }

    // Fonctions helper
    function getPersonaLabel(side) {
        var personas = {
            "economie_emplois": side === "left" ? "⚡ Tech-Optimiste" : "🤝 Syndicaliste",
            "education_ia": side === "left" ? "📚 Pédagogue IA" : "👨‍🏫 Humaniste", 
            "sante_diagnostic": side === "left" ? "⚕️ Médecin Pro-IA" : "👨‍⚕️ Médecin Humaniste",
            "surveillance_securite": side === "left" ? "👁️ Pro-Sécurité" : "🔒 Défenseur Privé",
            "art_creation": side === "left" ? "🎨 Pro-IA Art" : "🎭 Artiste Humain"
        }
        
        if (selectedDomain && personas[selectedDomain]) {
            return personas[selectedDomain]
        }
        
        return side === "left" ? "Optimiste Tech 2025 🔥" : "Sceptique Tech 2025 💀"
    }

    // Connexions backend
    Connections {
        target: backend
        
        function onThemeGenerated(theme) {
            generatedTheme = theme
            topicInput.text = theme
        }
        
        function onMessageStreamReceived(agentType, content, roundNum) {
            if (agentType === "agent_one") {
                if (roundNum > agent1Round) {
                    if (agent1Round > 0) leftTextArea.text += "\n\n"
                    leftTextArea.text += "[Round " + roundNum + "]\n"
                    agent1Round = roundNum
                }
                leftTextArea.text += content
                // Animation enlevée (plus d'avatar)
            } else if (agentType === "agent_two") {
                if (roundNum > agent2Round) {
                    if (agent2Round > 0) rightTextArea.text += "\n\n"
                    rightTextArea.text += "[Round " + roundNum + "]\n"
                    agent2Round = roundNum
                }
                rightTextArea.text += content
                // Animation enlevée (plus d'avatar)
            } else if (agentType === "moderator") {
                if (roundNum > moderatorRound) {
                    if (moderatorRound > 0) moderatorTextArea.text += "\n\n"
                    if (roundNum > 0) moderatorTextArea.text += "[Intervention " + roundNum + "]\n"
                    moderatorRound = roundNum
                }
                moderatorTextArea.text += content
            }
        }
        
        // NOUVEAU: Gestion fact-check
        function onFactCheckUpdate(agentType, result) {
            factCheckArea.text += "\n" + result + "\n"
        }
        
        function onSearchStarted(agentType, searchInfo) {
            if (agentType === "agent_one") {
                leftSearchLabel.text = searchInfo
            } else if (agentType === "agent_two") {
                rightSearchLabel.text = searchInfo
            }
        }
        
        function onMessageCompleted(agentType, fullMessage, roundNum) {
            if (agentType === "agent_one") {
                leftSearchLabel.text = ""
            } else if (agentType === "agent_two") {
                rightSearchLabel.text = ""
            }
        }
        
        function onDebateStatusChanged(isRunning) {
            debateRunning = isRunning
        }
        
        function onDebateFinished() {
            var separator = "=============================="
            leftTextArea.text += "\n\n" + separator + "\n🏁 FIN DE L'ÉMISSION!\n" + separator
            rightTextArea.text += "\n\n" + separator + "\n🏁 FIN DE L'ÉMISSION!\n" + separator
            if (moderatorEnabled) {
                moderatorTextArea.text += "\n\n" + separator + "\n📺 MERCI DE NOUS AVOIR SUIVIS!\n" + separator
            }
            factCheckArea.text += "\n📊 FACT-CHECK TERMINÉ"
        }
        
        function onErrorOccurred(error) {
            leftTextArea.text += "\n\n❌ ERREUR: " + error
            rightTextArea.text += "\n\n❌ ERREUR: " + error
            moderatorTextArea.text += "\n\n❌ ERREUR TECHNIQUE: " + error
        }
    }
}