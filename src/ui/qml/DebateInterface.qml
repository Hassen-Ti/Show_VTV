import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Layouts
import QtQuick.Particles

ApplicationWindow {
    id: mainWindow
    visible: true
    width: 1400
    height: 900
    title: "Multi-Tool Agent Debate Interface - TV Studio"
    color: "#001122"

    // Properties for tracking state
    property bool debateRunning: false
    property string agent1Name: "Agent One"
    property string agent2Name: "Agent Two"
    property bool customizationVisible: false
    property bool moderatorEnabled: true
    property int agent1Round: 0
    property int agent2Round: 0
    property int moderatorRound: 0
    property string generatedTheme: ""

    // Background
    Image {
        id: bgImage
        anchors.fill: parent
        source: "versus.png"
        fillMode: Image.PreserveAspectCrop
        opacity: 0.3
    }

    // Main content
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 20
        spacing: 20

        // Header - just spacing, background image speaks for itself
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 40
            color: "transparent"
        }

        // Theme generation section
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
                spacing: 10
                
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
                    Layout.preferredWidth: 300
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
                    text: "🎬 Générer Thème"
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

        // Main debate area
        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 20

            // Left Agent Panel
            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.preferredWidth: 400
                color: "transparent"
                
                ColumnLayout {
                    anchors.fill: parent
                    spacing: 10

                    // Avatar
                    Item {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 100
                        
                        AnimatedImage {
                            id: leftAvatar
                            anchors.centerIn: parent
                            width: 80
                            height: 80
                            source: "avatar_blue.gif"
                            playing: debateRunning
                            
                            onStatusChanged: {
                                if (status == Image.Error) {
                                    source = "avatar_blue_static.png"
                                }
                            }
                            
                            Rectangle {
                                id: leftGlow
                                anchors.centerIn: parent
                                width: parent.width + 20
                                height: parent.height + 20
                                radius: width / 2
                                color: "transparent"
                                border.color: "#00aaff"
                                border.width: 3
                                opacity: 0
                                
                                SequentialAnimation on opacity {
                                    id: leftGlowAnim
                                    running: false
                                    NumberAnimation { to: 0.8; duration: 200 }
                                    NumberAnimation { to: 0; duration: 400 }
                                }
                            }
                        }
                    }

                    // Customization Panel
                    Rectangle {
                        id: leftCustomPanel
                        Layout.fillWidth: true
                        Layout.preferredHeight: customizationVisible ? 180 : 0
                        visible: customizationVisible
                        color: "#001a33"
                        border.color: "#00aaff"
                        border.width: 1
                        radius: 5
                        
                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: 10
                            
                            Label {
                                text: "Customize Agent One"
                                color: "#00aaff"
                                font.bold: true
                                font.pixelSize: 14
                            }
                            
                            RowLayout {
                                Layout.fillWidth: true
                                
                                Label {
                                    text: "Name:"
                                    color: "#00aaff"
                                    Layout.preferredWidth: 60
                                }
                                
                                TextField {
                                    id: leftNameInput
                                    Layout.fillWidth: true
                                    text: "Agent One"
                                    placeholderText: "Enter agent name..."
                                    color: "#00ffff"
                                    font.family: "Consolas"
                                    
                                    background: Rectangle {
                                        color: "#002244"
                                        border.color: "#00aaff"
                                        radius: 3
                                    }
                                    
                                    onTextChanged: {
                                        agent1Name = text || "Agent One"
                                    }
                                }
                            }
                            
                            Label {
                                text: "Custom Prompt:"
                                color: "#00aaff"
                            }
                            
                            ScrollView {
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                
                                TextArea {
                                    id: leftPromptInput
                                    text: backend ? backend.getOptimisticPrompt() : "Tu es un fervent optimiste technologique..."
                                    wrapMode: TextArea.Wrap
                                    color: "#00ffff"
                                    selectByMouse: true
                                    font.family: "Consolas"
                                    font.pixelSize: 11
                                    
                                    background: Rectangle {
                                        color: "#002244"
                                        border.color: "#00aaff"
                                        radius: 3
                                    }
                                }
                            }
                        }
                    }

                    // Agent Label
                    Label {
                        id: leftLabel
                        Layout.fillWidth: true
                        text: agent1Name + " (Tech Optimist 🔥)"
                        color: "#00aaff"
                        font.pixelSize: 16
                        font.bold: true
                        font.family: "Consolas"
                        horizontalAlignment: Text.AlignHCenter
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

                    // Message Display
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
                                text: "Agent One responses will appear here..."
                                
                                background: Rectangle {
                                    color: "transparent"
                                }
                            }
                        }
                    }
                }
            }

            // Center Moderator Panel
            Rectangle {
                Layout.preferredWidth: 500
                Layout.fillHeight: true
                color: "transparent"
                
                ColumnLayout {
                    anchors.fill: parent
                    spacing: 10
                    
                    // Moderator Avatar/Logo
                    Item {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 120
                        
                        Rectangle {
                            anchors.centerIn: parent
                            width: 100
                            height: 100
                            radius: 50
                            color: Qt.rgba(1, 0.8, 0, 0.2)
                            border.color: "#ffcc00"
                            border.width: 3
                            
                            Text {
                                anchors.centerIn: parent
                                text: "🎙️"
                                font.pixelSize: 50
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
                    
                    // Moderator Label
                    Label {
                        Layout.fillWidth: true
                        text: "📺 ANIMATEUR TV"
                        color: "#ffcc00"
                        font.pixelSize: 18
                        font.bold: true
                        font.family: "Consolas"
                        horizontalAlignment: Text.AlignHCenter
                    }
                    
                    // Toggle Moderator
                    Switch {
                        id: moderatorSwitch
                        Layout.alignment: Qt.AlignHCenter
                        checked: true
                        text: checked ? "Animateur ON" : "Animateur OFF"
                        palette.text: "#ffcc00"
                        
                        onCheckedChanged: {
                            moderatorEnabled = checked
                        }
                    }
                    
                    // Generated Theme Display
                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 80
                        color: Qt.rgba(0.8, 0.6, 0, 0.1)
                        border.color: "#ffcc00"
                        border.width: 1
                        radius: 8
                        visible: generatedTheme !== ""
                        
                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: 10
                            
                            Label {
                                text: "📋 Thème du débat:"
                                color: "#ffcc00"
                                font.bold: true
                                font.pixelSize: 12
                            }
                            
                            Text {
                                id: themeText
                                Layout.fillWidth: true
                                text: generatedTheme
                                color: "#ffffff"
                                font.pixelSize: 14
                                font.family: "Consolas"
                                wrapMode: Text.Wrap
                            }
                        }
                    }
                    
                    // Moderator Messages
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
                                text: moderatorEnabled ? "🎬 L'animateur est prêt à lancer le débat..." : "Mode débat direct (sans animateur)"
                                
                                background: Rectangle {
                                    color: "transparent"
                                }
                            }
                        }
                    }
                }
            }

            // Right Agent Panel
            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.preferredWidth: 400
                color: "transparent"
                
                ColumnLayout {
                    anchors.fill: parent
                    spacing: 10

                    // Avatar
                    Item {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 100
                        
                        AnimatedImage {
                            id: rightAvatar
                            anchors.centerIn: parent
                            width: 80
                            height: 80
                            source: "avatar_red.gif"
                            playing: debateRunning
                            
                            onStatusChanged: {
                                if (status == Image.Error) {
                                    source: "avatar_red_static.png"
                                }
                            }
                            
                            Rectangle {
                                id: rightGlow
                                anchors.centerIn: parent
                                width: parent.width + 20
                                height: parent.height + 20
                                radius: width / 2
                                color: "transparent"
                                border.color: "#ff4444"
                                border.width: 3
                                opacity: 0
                                
                                SequentialAnimation on opacity {
                                    id: rightGlowAnim
                                    running: false
                                    NumberAnimation { to: 0.8; duration: 200 }
                                    NumberAnimation { to: 0; duration: 400 }
                                }
                            }
                        }
                    }

                    // Customization Panel
                    Rectangle {
                        id: rightCustomPanel
                        Layout.fillWidth: true
                        Layout.preferredHeight: customizationVisible ? 180 : 0
                        visible: customizationVisible
                        color: "#331a1a"
                        border.color: "#ff4444"
                        border.width: 1
                        radius: 5
                        
                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: 10
                            
                            Label {
                                text: "Customize Agent Two"
                                color: "#ff4444"
                                font.bold: true
                                font.pixelSize: 14
                            }
                            
                            RowLayout {
                                Layout.fillWidth: true
                                
                                Label {
                                    text: "Name:"
                                    color: "#ff4444"
                                    Layout.preferredWidth: 60
                                }
                                
                                TextField {
                                    id: rightNameInput
                                    Layout.fillWidth: true
                                    text: "Agent Two"
                                    placeholderText: "Enter agent name..."
                                    color: "#ff6666"
                                    font.family: "Consolas"
                                    
                                    background: Rectangle {
                                        color: "#442222"
                                        border.color: "#ff4444"
                                        radius: 3
                                    }
                                    
                                    onTextChanged: {
                                        agent2Name = text || "Agent Two"
                                    }
                                }
                            }
                            
                            Label {
                                text: "Custom Prompt:"
                                color: "#ff4444"
                            }
                            
                            ScrollView {
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                
                                TextArea {
                                    id: rightPromptInput
                                    text: backend ? backend.getCautiousPrompt() : "Tu es un sceptique technologique féroce..."
                                    wrapMode: TextArea.Wrap
                                    color: "#ff6666"
                                    selectByMouse: true
                                    font.family: "Consolas"
                                    font.pixelSize: 11
                                    
                                    background: Rectangle {
                                        color: "#442222"
                                        border.color: "#ff4444"
                                        radius: 3
                                    }
                                }
                            }
                        }
                    }

                    // Agent Label
                    Label {
                        id: rightLabel
                        Layout.fillWidth: true
                        text: agent2Name + " (Tech Skeptic 💀)"
                        color: "#ff4444"
                        font.pixelSize: 16
                        font.bold: true
                        font.family: "Consolas"
                        horizontalAlignment: Text.AlignHCenter
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

                    // Message Display
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
                                text: "Agent Two responses will appear here..."
                                
                                background: Rectangle {
                                    color: "transparent"
                                }
                            }
                        }
                    }
                }
            }
        }

        // Bottom controls
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 100
            color: Qt.rgba(0, 0.067, 0.133, 0.7)
            border.color: "#00ffff"
            border.width: 1
            radius: 10
            
            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 15
                spacing: 10
                
                // Topic input
                RowLayout {
                    Layout.fillWidth: true
                    
                    Label {
                        text: "Question finale:"
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
                }
                
                // Control buttons
                RowLayout {
                    Layout.fillWidth: true
                    Layout.alignment: Qt.AlignHCenter
                    spacing: 20
                    
                    Button {
                        id: toggleCustomBtn
                        text: "⚙️ " + (customizationVisible ? "Masquer" : "Afficher") + " Options"
                        font.pixelSize: 14
                        font.bold: true
                        font.family: "Consolas"
                        palette.buttonText: "#00ffff"
                        
                        background: Rectangle {
                            color: parent.hovered ? "#003366" : "#001a33"
                            border.color: "#00ffff"
                            border.width: 2
                            radius: 8
                        }
                        
                        onClicked: {
                            customizationVisible = !customizationVisible
                        }
                    }
                    
                    Button {
                        id: startBtn
                        text: debateRunning ? "⚡ DÉBAT EN COURS..." : "🚀 LANCER LE DÉBAT"
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
                            // Clear previous content
                            leftTextArea.text = "🔥 Préparation..."
                            rightTextArea.text = "💀 Préparation..."
                            moderatorTextArea.text = moderatorEnabled ? "🎬 L'animateur prépare le plateau..." : ""
                            agent1Round = 0
                            agent2Round = 0
                            moderatorRound = 0
                            
                            // Use generated theme if available, otherwise use input
                            var finalTopic = topicInput.text || generatedTheme || (backend ? backend.getDefaultTopic() : "Devons-nous faire confiance à l'IA?")
                            
                            // Start debate with moderator setting
                            backend.startDebate(
                                finalTopic,
                                leftPromptInput.text,
                                rightPromptInput.text,
                                moderatorEnabled
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
    }

    // Backend connections
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
                leftGlowAnim.restart()
            } else if (agentType === "agent_two") {
                if (roundNum > agent2Round) {
                    if (agent2Round > 0) rightTextArea.text += "\n\n"
                    rightTextArea.text += "[Round " + roundNum + "]\n"
                    agent2Round = roundNum
                }
                rightTextArea.text += content
                rightGlowAnim.restart()
            } else if (agentType === "moderator") {
                if (roundNum > moderatorRound) {
                    if (moderatorRound > 0) moderatorTextArea.text += "\n\n"
                    if (roundNum > 0) moderatorTextArea.text += "[Intervention " + roundNum + "]\n"
                    moderatorRound = roundNum
                }
                moderatorTextArea.text += content
            }
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
            var separator = "==============================";
            leftTextArea.text += "\n\n" + separator + "\n🏁 FIN DU DÉBAT!\n" + separator
            rightTextArea.text += "\n\n" + separator + "\n🏁 FIN DU DÉBAT!\n" + separator
            if (moderatorEnabled) {
                moderatorTextArea.text += "\n\n" + separator + "\n📺 ÉMISSION TERMINÉE!\n" + separator
            }
        }
        
        function onErrorOccurred(error) {
            leftTextArea.text += "\n\n❌ ERREUR: " + error
            rightTextArea.text += "\n\n❌ ERREUR: " + error
            moderatorTextArea.text += "\n\n❌ ERREUR TECHNIQUE: " + error
        }
    }
}