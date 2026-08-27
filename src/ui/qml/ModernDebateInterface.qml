import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Layouts

ApplicationWindow {
    id: mainWindow
    visible: true
    width: 1400
    height: 900
    minimumWidth: 1100
    minimumHeight: 720
    title: "Show V.TV — Plateau en direct"
    color: theme.bg

    // ------------------------------------------------------------------
    // Design tokens
    // ------------------------------------------------------------------
    QtObject {
        id: theme

        readonly property color bg: "#070B12"
        readonly property color bgRaised: "#0C121D"
        readonly property color panel: "#0D1320"
        readonly property color panelSoft: "#111927"
        readonly property color line: "#1E2838"
        readonly property color lineSoft: "#18202E"

        readonly property color ink: "#E8ECF4"
        readonly property color inkDim: "#8B95A7"
        readonly property color inkFaint: "#5C6678"
        readonly property color feedText: "#CBD3E1"

        readonly property color blue: "#4DA3FF"
        readonly property color coral: "#FF6257"
        readonly property color gold: "#E5B54D"
        readonly property color live: "#FF2E44"

        readonly property string display: "Bahnschrift"
        readonly property string body: "Segoe UI"
        readonly property string mono: "Consolas"
    }

    // ------------------------------------------------------------------
    // State
    // ------------------------------------------------------------------
    property bool debateRunning: false
    property bool spectatorMode: true
    property bool regieVisible: false
    property string leftGuestName: "Invité A"
    property string rightGuestName: "Invité B"
    property bool backstageVisible: !spectatorMode
    property bool customizationVisible: false
    property int agent1Round: 0
    property int agent2Round: 0
    property int moderatorRound: 0
    property string generatedTheme: ""
    property string selectedDomain: ""
    property string currentSpeaker: ""
    property string audienceQuestionPending: ""
    property bool audienceQuestionWasRead: false
    // File oreillette (max 3 côté bridge) — hint UX si pleine / en attente.
    property int audienceQueueDepth: 0
    property int audienceQueueCapacity: 3
    property string audienceHint: ""
    // Les zones affichent un texte d'attente qu'on efface au premier flux réel.
    property bool leftFeedPristine: true
    property bool rightFeedPristine: true
    property bool modFeedPristine: true

    readonly property bool inRegie: !spectatorMode || regieVisible

    // ------------------------------------------------------------------
    // Background: quiet studio gradient
    // ------------------------------------------------------------------
    Rectangle {
        anchors.fill: parent
        gradient: Gradient {
            GradientStop { position: 0.0; color: theme.bgRaised }
            GradientStop { position: 0.45; color: theme.bg }
            GradientStop { position: 1.0; color: "#05080D" }
        }
    }

    // ------------------------------------------------------------------
    // Reusable pieces
    // ------------------------------------------------------------------
    component Eyebrow: Text {
        font.family: theme.display
        font.pixelSize: 10
        font.letterSpacing: 2.4
        font.weight: Font.DemiBold
        color: theme.inkFaint
    }

    component StudioField: TextField {
        id: field
        color: theme.ink
        font.family: theme.body
        font.pixelSize: 14
        placeholderTextColor: theme.inkFaint
        leftPadding: 12
        rightPadding: 12
        selectionColor: Qt.alpha(theme.blue, 0.45)
        background: Rectangle {
            color: theme.bg
            border.color: field.activeFocus ? theme.gold : theme.line
            border.width: 1
            radius: 6
            Behavior on border.color { ColorAnimation { duration: 150 } }
        }
    }

    component StudioSwitch: Switch {
        id: sw
        property color accent: theme.gold
        indicator: Rectangle {
            implicitWidth: 36
            implicitHeight: 18
            y: (sw.height - height) / 2
            radius: 9
            color: sw.checked ? Qt.alpha(sw.accent, 0.28) : theme.panelSoft
            border.color: sw.checked ? sw.accent : theme.line
            border.width: 1
            Rectangle {
                width: 12
                height: 12
                radius: 6
                y: 3
                x: sw.checked ? parent.width - width - 3 : 3
                color: sw.checked ? sw.accent : theme.inkFaint
                Behavior on x { NumberAnimation { duration: 130; easing.type: Easing.OutCubic } }
            }
        }
        contentItem: Text {
            text: sw.text
            font.family: theme.display
            font.pixelSize: 11
            font.letterSpacing: 1.2
            color: sw.checked ? theme.ink : theme.inkDim
            verticalAlignment: Text.AlignVCenter
            leftPadding: sw.indicator.width + 8
        }
        // Visible keyboard focus
        Rectangle {
            anchors.fill: parent
            anchors.margins: -2
            radius: 6
            color: "transparent"
            border.color: theme.gold
            border.width: sw.visualFocus ? 1 : 0
        }
    }

    // ------------------------------------------------------------------
    // Layout
    // ------------------------------------------------------------------
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 22
        spacing: 14

        // ============================================================
        // Masthead — show identity + on-air state
        // ============================================================
        Item {
            Layout.fillWidth: true
            Layout.preferredHeight: 46

            RowLayout {
                anchors.fill: parent
                spacing: 16

                // Logo block
                Row {
                    spacing: 8
                    Text {
                        text: "SHOW"
                        anchors.verticalCenter: parent.verticalCenter
                        font.family: theme.display
                        font.pixelSize: 24
                        font.weight: Font.Bold
                        font.letterSpacing: 4
                        color: theme.ink
                    }
                    Rectangle {
                        width: vtvText.implicitWidth + 16
                        height: 30
                        anchors.verticalCenter: parent.verticalCenter
                        radius: 4
                        color: theme.live
                        Text {
                            id: vtvText
                            anchors.centerIn: parent
                            text: "V.TV"
                            font.family: theme.display
                            font.pixelSize: 16
                            font.weight: Font.Bold
                            font.letterSpacing: 2
                            color: "#FFFFFF"
                        }
                    }
                }

                Rectangle { width: 1; height: 24; color: theme.line }

                // Live badge
                Row {
                    spacing: 8
                    Rectangle {
                        id: liveDot
                        width: 9
                        height: 9
                        radius: 4.5
                        anchors.verticalCenter: parent.verticalCenter
                        color: debateRunning ? theme.live : theme.inkFaint
                        SequentialAnimation on opacity {
                            running: debateRunning
                            loops: Animation.Infinite
                            NumberAnimation { from: 1.0; to: 0.25; duration: 700; easing.type: Easing.InOutSine }
                            NumberAnimation { from: 0.25; to: 1.0; duration: 700; easing.type: Easing.InOutSine }
                        }
                        onVisibleChanged: opacity = 1
                    }
                    Text {
                        anchors.verticalCenter: parent.verticalCenter
                        text: debateRunning ? "EN DIRECT" : "HORS ANTENNE"
                        font.family: theme.display
                        font.pixelSize: 12
                        font.letterSpacing: 2.4
                        font.weight: Font.DemiBold
                        color: debateRunning ? theme.live : theme.inkDim
                    }
                }

                Item { Layout.fillWidth: true }

                // Round counter
                Text {
                    visible: debateRunning
                    text: "MANCHE " + Math.max(agent1Round, agent2Round, 1)
                    font.family: theme.display
                    font.pixelSize: 13
                    font.letterSpacing: 2
                    font.weight: Font.DemiBold
                    color: theme.gold
                }

                // Toggle régie : état coché = panneaux producteur visibles
                // (label fixe « RÉGIE », cohérent avec le switch COULISSES).
                Button {
                    id: regieToggle
                    Layout.preferredHeight: 28
                    Layout.preferredWidth: regieToggle.implicitWidth
                    checkable: true
                    checked: regieVisible
                    text: "RÉGIE"
                    visible: spectatorMode
                    Accessible.name: regieVisible
                                 ? "Fermer la régie, mode spectateur"
                                 : "Ouvrir la régie"

                    contentItem: Text {
                        text: regieToggle.text
                        font.family: theme.display
                        font.pixelSize: 10
                        font.letterSpacing: 1.6
                        font.weight: Font.DemiBold
                        color: regieVisible ? theme.gold : theme.inkDim
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                        leftPadding: 10
                        rightPadding: 10
                    }
                    background: Rectangle {
                        color: regieVisible ? Qt.alpha(theme.gold, 0.12) : "transparent"
                        border.color: regieVisible ? theme.gold : theme.line
                        border.width: 1
                        radius: 4
                        Behavior on border.color { ColorAnimation { duration: 150 } }
                        Behavior on color { ColorAnimation { duration: 150 } }
                    }
                    onClicked: {
                        regieVisible = !regieVisible
                        checked = regieVisible
                        if (!regieVisible) {
                            // Resync coulisses : éviter switch ON + panneau fermé.
                            backstageVisible = false
                            if (backstageSwitch.checked)
                                backstageSwitch.checked = false
                        }
                    }
                }
            }
        }

        // ============================================================
        // Régie — setup strip (masquée en mode spectateur)
        // ============================================================
        Rectangle {
            id: regieStrip
            Layout.fillWidth: true
            Layout.preferredHeight: inRegie ? 66 : 0
            visible: Layout.preferredHeight > 0
            clip: true
            color: theme.panel
            border.color: theme.line
            border.width: 1
            radius: 8

            Behavior on Layout.preferredHeight {
                NumberAnimation { duration: 220; easing.type: Easing.OutCubic }
            }

            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: 16
                anchors.rightMargin: 16
                spacing: 14

                ColumnLayout {
                    spacing: 2
                    Eyebrow { text: "RÉGIE" }
                    Text {
                        text: "Préparation"
                        font.family: theme.body
                        font.pixelSize: 12
                        color: theme.inkDim
                    }
                }

                Rectangle { width: 1; height: 34; color: theme.lineSoft }

                ComboBox {
                    id: personaSelector
                    Layout.preferredWidth: 230
                    Layout.preferredHeight: 36
                    model: ["Débat libre", "Économie & emplois", "Éducation & IA", "Santé & diagnostic", "Surveillance & IA", "Création artistique"]

                    background: Rectangle {
                        color: theme.bg
                        border.color: personaSelector.activeFocus || personaSelector.popup.visible ? theme.gold : theme.line
                        border.width: 1
                        radius: 6
                        Behavior on border.color { ColorAnimation { duration: 150 } }
                    }
                    contentItem: Text {
                        text: personaSelector.displayText
                        color: theme.ink
                        font.family: theme.body
                        font.pixelSize: 13
                        verticalAlignment: Text.AlignVCenter
                        elide: Text.ElideRight
                        leftPadding: 12
                        rightPadding: 26
                    }
                    indicator: Text {
                        x: personaSelector.width - width - 10
                        y: (personaSelector.height - height) / 2
                        text: "\u25BE"
                        font.pixelSize: 11
                        color: theme.inkDim
                    }
                    delegate: ItemDelegate {
                        id: personaDelegate
                        required property var model
                        required property int index
                        width: ListView.view ? ListView.view.width : implicitWidth
                        height: 32
                        highlighted: personaSelector.highlightedIndex === index
                        contentItem: Text {
                            text: personaDelegate.model[personaSelector.textRole === "" ? "modelData" : personaSelector.textRole]
                            color: personaDelegate.highlighted ? theme.ink : theme.inkDim
                            font.family: theme.body
                            font.pixelSize: 13
                            verticalAlignment: Text.AlignVCenter
                            leftPadding: 8
                        }
                        background: Rectangle {
                            color: personaDelegate.highlighted ? theme.panelSoft : "transparent"
                            radius: 4
                        }
                    }
                    popup: Popup {
                        y: personaSelector.height + 4
                        width: personaSelector.width
                        padding: 4
                        background: Rectangle {
                            color: theme.panel
                            border.color: theme.line
                            border.width: 1
                            radius: 8
                        }
                        contentItem: ListView {
                            clip: true
                            implicitHeight: contentHeight
                            model: personaSelector.popup.visible ? personaSelector.delegateModel : null
                            currentIndex: personaSelector.highlightedIndex
                        }
                    }

                    onCurrentIndexChanged: {
                        var domains = ["", "economie_emplois", "education_ia", "sante_diagnostic", "surveillance_securite", "art_creation"]
                        selectedDomain = domains[currentIndex]

                        if (currentIndex > 0) {
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
                        refreshGuestNames()
                    }
                }

                StudioField {
                    id: themeInput
                    Layout.fillWidth: true
                    Layout.preferredHeight: 36
                    text: backend ? backend.getDefaultUserTopic() : "Intelligence artificielle et société"
                    placeholderText: "Thématique de l'émission — ex. Intelligence artificielle, environnement…"
                }

                Button {
                    id: generateBtn
                    Layout.preferredHeight: 36
                    text: "Générer le sujet"
                    contentItem: Text {
                        text: generateBtn.text
                        font.family: theme.display
                        font.pixelSize: 12
                        font.letterSpacing: 1.2
                        font.weight: Font.DemiBold
                        color: theme.gold
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                        leftPadding: 14
                        rightPadding: 14
                    }
                    background: Rectangle {
                        color: generateBtn.hovered ? Qt.alpha(theme.gold, 0.14) : "transparent"
                        border.color: generateBtn.visualFocus ? theme.ink : Qt.alpha(theme.gold, 0.55)
                        border.width: 1
                        radius: 6
                        Behavior on color { ColorAnimation { duration: 120 } }
                    }
                    onClicked: backend.generateTheme(themeInput.text)
                }
            }
        }

        // ============================================================
        // Plateau — three seats
        // ============================================================
        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 14

            // ---------------- Left debater ----------------
            Rectangle {
                id: leftCard
                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.preferredWidth: 420
                property bool speaking: currentSpeaker === "agent_one"
                color: theme.panel
                border.color: speaking ? theme.blue : theme.line
                border.width: 1
                radius: 10
                Behavior on border.color { ColorAnimation { duration: 250 } }

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 14
                    spacing: 10

                    // Nameplate
                    RowLayout {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 38
                        Layout.maximumHeight: 38
                        spacing: 10
                        Rectangle {
                            width: 4
                            Layout.fillHeight: true
                            radius: 2
                            color: theme.blue
                        }
                        ColumnLayout {
                            spacing: 1
                            Eyebrow { text: "POUR"; color: Qt.alpha(theme.blue, 0.75) }
                            Text {
                                id: leftLabel
                                text: leftGuestName
                                color: theme.ink
                                font.family: theme.display
                                font.pixelSize: 17
                                font.weight: Font.DemiBold
                                font.letterSpacing: 0.5
                                elide: Text.ElideRight
                                Layout.fillWidth: true
                            }
                        }
                        Item { Layout.fillWidth: true }
                        Row {
                            spacing: 6
                            visible: leftCard.speaking
                            Rectangle {
                                width: 7; height: 7; radius: 3.5
                                anchors.verticalCenter: parent.verticalCenter
                                color: theme.blue
                                SequentialAnimation on opacity {
                                    running: leftCard.speaking
                                    loops: Animation.Infinite
                                    NumberAnimation { from: 1; to: 0.3; duration: 500 }
                                    NumberAnimation { from: 0.3; to: 1; duration: 500 }
                                }
                            }
                            Text {
                                text: "PAROLE"
                                anchors.verticalCenter: parent.verticalCenter
                                font.family: theme.display
                                font.pixelSize: 10
                                font.letterSpacing: 2
                                color: theme.blue
                            }
                        }
                    }

                    // Search indicator
                    Text {
                        id: leftSearchLabel
                        Layout.fillWidth: true
                        text: ""
                        color: theme.inkDim
                        font.family: theme.body
                        font.pixelSize: 11
                        font.italic: true
                        elide: Text.ElideRight
                        visible: text !== ""
                    }

                    Rectangle { Layout.fillWidth: true; height: 1; color: theme.lineSoft }

                    // Feed
                    ScrollView {
                        Layout.fillWidth: true
                        Layout.fillHeight: true

                        TextArea {
                            id: leftTextArea
                            readOnly: true
                            wrapMode: TextArea.Wrap
                            color: theme.feedText
                            font.pixelSize: 14
                            font.family: theme.body
                            selectByMouse: true
                            selectionColor: Qt.alpha(theme.blue, 0.4)
                            text: "En attente du direct."
                            background: Rectangle { color: "transparent" }
                            onTextChanged: cursorPosition = length
                        }
                    }
                }
            }

            // ---------------- Center: host + fact-check ----------------
            Rectangle {
                id: hostCard
                Layout.preferredWidth: 470
                Layout.fillHeight: true
                property bool speaking: currentSpeaker === "moderator"
                property bool readingAudience: audienceQuestionWasRead && speaking
                color: theme.panel
                border.color: readingAudience ? theme.gold : (speaking ? theme.gold : theme.line)
                border.width: readingAudience ? 2 : 1
                radius: 10
                Behavior on border.color { ColorAnimation { duration: 250 } }
                Behavior on border.width { NumberAnimation { duration: 250 } }

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 14
                    spacing: 10

                    // Host nameplate
                    RowLayout {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 38
                        Layout.maximumHeight: 38
                        spacing: 10
                        Rectangle {
                            width: 4
                            Layout.fillHeight: true
                            radius: 2
                            color: theme.gold
                        }
                        ColumnLayout {
                            spacing: 1
                            Eyebrow {
                                text: hostCard.readingAudience ? "QUESTION DU PUBLIC" : "ANIMATEUR"
                                color: Qt.alpha(theme.gold, 0.75)
                            }
                            Text {
                                text: "Mr Bullshit"
                                color: theme.ink
                                font.family: theme.display
                                font.pixelSize: 17
                                font.weight: Font.DemiBold
                                font.letterSpacing: 0.5
                            }
                        }
                        Item { Layout.fillWidth: true }
                        Row {
                            spacing: 6
                            visible: hostCard.speaking
                            Rectangle {
                                width: 7; height: 7; radius: 3.5
                                anchors.verticalCenter: parent.verticalCenter
                                color: theme.gold
                                SequentialAnimation on opacity {
                                    running: hostCard.speaking
                                    loops: Animation.Infinite
                                    NumberAnimation { from: 1; to: 0.3; duration: 500 }
                                    NumberAnimation { from: 0.3; to: 1; duration: 500 }
                                }
                            }
                            Text {
                                text: "PAROLE"
                                anchors.verticalCenter: parent.verticalCenter
                                font.family: theme.display
                                font.pixelSize: 10
                                font.letterSpacing: 2
                                color: theme.gold
                            }
                        }
                    }

                    // Coulisses toggle
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 18

                        StudioSwitch {
                            id: backstageSwitch
                            checked: backstageVisible
                            text: "COULISSES"
                            accent: theme.gold
                            visible: inRegie
                            onCheckedChanged: {
                                if (backstageVisible !== checked)
                                    backstageVisible = checked
                            }
                        }
                        Item { Layout.fillWidth: true }
                    }

                    Rectangle { Layout.fillWidth: true; height: 1; color: theme.lineSoft }

                    // Host feed
                    ScrollView {
                        Layout.fillWidth: true
                        Layout.fillHeight: true

                        TextArea {
                            id: moderatorTextArea
                            readOnly: true
                            wrapMode: TextArea.Wrap
                            color: theme.feedText
                            font.pixelSize: 14
                            font.family: theme.body
                            selectByMouse: true
                            selectionColor: Qt.alpha(theme.gold, 0.4)
                            text: "Prêt pour le direct."
                            background: Rectangle { color: "transparent" }
                            onTextChanged: cursorPosition = length
                        }
                    }

                    // Bandeau coulisses (monologues, tension)
                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: backstageVisible ? 132 : 0
                        visible: Layout.preferredHeight > 0
                        clip: true
                        color: theme.bg
                        border.color: theme.lineSoft
                        border.width: 1
                        radius: 8

                        Behavior on Layout.preferredHeight {
                            NumberAnimation { duration: 250; easing.type: Easing.OutCubic }
                        }

                        RowLayout {
                            anchors.fill: parent
                            anchors.margins: 10
                            spacing: 10

                            // Wire label plate
                            ColumnLayout {
                                Layout.preferredWidth: 92
                                Layout.fillHeight: true
                                spacing: 6
                                Eyebrow {
                                    text: "COULISSES"
                                    font.letterSpacing: 1.4
                                    color: Qt.alpha(theme.gold, 0.8)
                                }
                                Rectangle {
                                    width: 26; height: 3; radius: 1.5
                                    color: Qt.alpha(theme.gold, 0.5)
                                }
                                Item { Layout.fillHeight: true }
                            }

                            Rectangle { width: 1; Layout.fillHeight: true; color: theme.lineSoft }

                            ScrollView {
                                Layout.fillWidth: true
                                Layout.fillHeight: true

                                TextArea {
                                    id: backstageArea
                                    readOnly: true
                                    wrapMode: TextArea.Wrap
                                    color: theme.inkDim
                                    font.pixelSize: 12
                                    font.family: theme.mono
                                    selectByMouse: true
                                    selectionColor: Qt.alpha(theme.gold, 0.4)
                                    text: "Pensées et métriques du plateau."
                                    background: Rectangle { color: "transparent" }
                                    onTextChanged: cursorPosition = length
                                }
                            }
                        }
                    }
                }
            }

            // ---------------- Right debater ----------------
            Rectangle {
                id: rightCard
                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.preferredWidth: 420
                property bool speaking: currentSpeaker === "agent_two"
                color: theme.panel
                border.color: speaking ? theme.coral : theme.line
                border.width: 1
                radius: 10
                Behavior on border.color { ColorAnimation { duration: 250 } }

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 14
                    spacing: 10

                    RowLayout {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 38
                        Layout.maximumHeight: 38
                        spacing: 10
                        Rectangle {
                            width: 4
                            Layout.fillHeight: true
                            radius: 2
                            color: theme.coral
                        }
                        ColumnLayout {
                            spacing: 1
                            Eyebrow { text: "CONTRE"; color: Qt.alpha(theme.coral, 0.75) }
                            Text {
                                id: rightLabel
                                text: rightGuestName
                                color: theme.ink
                                font.family: theme.display
                                font.pixelSize: 17
                                font.weight: Font.DemiBold
                                font.letterSpacing: 0.5
                                elide: Text.ElideRight
                                Layout.fillWidth: true
                            }
                        }
                        Item { Layout.fillWidth: true }
                        Row {
                            spacing: 6
                            visible: rightCard.speaking
                            Rectangle {
                                width: 7; height: 7; radius: 3.5
                                anchors.verticalCenter: parent.verticalCenter
                                color: theme.coral
                                SequentialAnimation on opacity {
                                    running: rightCard.speaking
                                    loops: Animation.Infinite
                                    NumberAnimation { from: 1; to: 0.3; duration: 500 }
                                    NumberAnimation { from: 0.3; to: 1; duration: 500 }
                                }
                            }
                            Text {
                                text: "PAROLE"
                                anchors.verticalCenter: parent.verticalCenter
                                font.family: theme.display
                                font.pixelSize: 10
                                font.letterSpacing: 2
                                color: theme.coral
                            }
                        }
                    }

                    Text {
                        id: rightSearchLabel
                        Layout.fillWidth: true
                        text: ""
                        color: theme.inkDim
                        font.family: theme.body
                        font.pixelSize: 11
                        font.italic: true
                        elide: Text.ElideRight
                        visible: text !== ""
                    }

                    Rectangle { Layout.fillWidth: true; height: 1; color: theme.lineSoft }

                    ScrollView {
                        Layout.fillWidth: true
                        Layout.fillHeight: true

                        TextArea {
                            id: rightTextArea
                            readOnly: true
                            wrapMode: TextArea.Wrap
                            color: theme.feedText
                            font.pixelSize: 14
                            font.family: theme.body
                            selectByMouse: true
                            selectionColor: Qt.alpha(theme.coral, 0.4)
                            text: "En attente du direct."
                            background: Rectangle { color: "transparent" }
                            onTextChanged: cursorPosition = length
                        }
                    }
                }
            }
        }

        // ============================================================
        // Oreillette — question du public
        // ============================================================
        Rectangle {
            id: audienceBar
            Layout.fillWidth: true
            Layout.preferredHeight: 58
            color: theme.panelSoft
            border.color: audienceQuestionPending !== "" ? Qt.alpha(theme.gold, 0.45) : theme.line
            border.width: 1
            radius: 8
            Behavior on border.color { ColorAnimation { duration: 200 } }

            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: 16
                anchors.rightMargin: 16
                spacing: 12

                ColumnLayout {
                    spacing: 2
                    Eyebrow { text: "PUBLIC"; color: Qt.alpha(theme.gold, 0.7) }
                    Text {
                        text: {
                            if (audienceHint !== "")
                                return audienceHint
                            if (audienceQueueDepth > 0)
                                return "En file (" + audienceQueueDepth + "/" + audienceQueueCapacity
                                       + ") — le modérateur décidera s'il relance"
                            return "Intervenir de loin"
                        }
                        font.family: theme.body
                        font.pixelSize: 11
                        color: audienceHint !== "" ? theme.coral : theme.inkDim
                    }
                }

                Rectangle { width: 1; height: 30; color: theme.lineSoft }

                StudioField {
                    id: audienceInput
                    Layout.fillWidth: true
                    Layout.preferredHeight: 36
                    placeholderText: "Poser une question au plateau…"
                    maximumLength: 280
                    onAccepted: audienceSendBtn.clicked()
                    onTextEdited: audienceHint = ""
                }

                Button {
                    id: audienceSendBtn
                    Layout.preferredHeight: 36
                    enabled: audienceInput.text.trim().length > 0
                    text: "Envoyer"

                    contentItem: Text {
                        text: audienceSendBtn.text
                        font.family: theme.display
                        font.pixelSize: 11
                        font.letterSpacing: 1.2
                        font.weight: Font.DemiBold
                        color: audienceSendBtn.enabled ? theme.gold : theme.inkFaint
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                        leftPadding: 14
                        rightPadding: 14
                    }
                    background: Rectangle {
                        color: audienceSendBtn.enabled
                               ? (audienceSendBtn.hovered ? Qt.alpha(theme.gold, 0.22) : Qt.alpha(theme.gold, 0.1))
                               : "transparent"
                        border.color: audienceSendBtn.enabled ? theme.gold : theme.lineSoft
                        border.width: 1
                        radius: 6
                    }
                    onClicked: {
                        if (!backend)
                            return
                        var ok = backend.submitAudienceQuestion(audienceInput.text)
                        if (ok) {
                            audienceQuestionPending = audienceInput.text.trim()
                            audienceInput.text = ""
                            audienceHint = ""
                            syncAudienceQueueDepth()
                        } else if (audienceInput.text.trim().length > 0) {
                            audienceHint = "File pleine — max " + audienceQueueCapacity + " questions"
                            syncAudienceQueueDepth()
                        }
                    }
                }
            }
        }

        // ============================================================
        // Control bar — question + on-air button
        // ============================================================
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 70
            color: theme.panel
            border.color: theme.line
            border.width: 1
            radius: 8

            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: 16
                anchors.rightMargin: 16
                spacing: 14

                ColumnLayout {
                    spacing: 2
                    visible: inRegie
                    Eyebrow { text: "SUJET" }
                    Text {
                        text: "Question du débat"
                        font.family: theme.body
                        font.pixelSize: 12
                        color: theme.inkDim
                    }
                }

                Rectangle {
                    width: 1; height: 34; color: theme.lineSoft
                    visible: inRegie
                }

                // En mode spectateur pur : sujet en lecture seule (pas de régie).
                Text {
                    Layout.fillWidth: true
                    visible: !inRegie
                    text: topicInput.text
                    color: theme.ink
                    font.family: theme.body
                    font.pixelSize: 14
                    elide: Text.ElideRight
                    verticalAlignment: Text.AlignVCenter
                }

                StudioField {
                    id: topicInput
                    Layout.fillWidth: true
                    Layout.preferredHeight: 38
                    visible: inRegie
                    text: generatedTheme || (backend ? backend.getDefaultTopic() : "Devons-nous faire confiance à l'IA?")
                    placeholderText: "Question posée aux débatteurs…"
                    readOnly: debateRunning
                }

                Button {
                    id: startBtn
                    Layout.preferredHeight: 40
                    enabled: !debateRunning
                    text: debateRunning ? "À L'ANTENNE" : "PASSER À L'ANTENNE"

                    contentItem: Row {
                        spacing: 8
                        leftPadding: 18
                        rightPadding: 18
                        Rectangle {
                            width: 8; height: 8; radius: 4
                            anchors.verticalCenter: parent.verticalCenter
                            color: startBtn.enabled ? "#FFFFFF" : theme.live
                            SequentialAnimation on opacity {
                                running: debateRunning
                                loops: Animation.Infinite
                                NumberAnimation { from: 1; to: 0.25; duration: 700 }
                                NumberAnimation { from: 0.25; to: 1; duration: 700 }
                            }
                        }
                        Text {
                            text: startBtn.text
                            anchors.verticalCenter: parent.verticalCenter
                            font.family: theme.display
                            font.pixelSize: 13
                            font.weight: Font.Bold
                            font.letterSpacing: 1.8
                            color: startBtn.enabled ? "#FFFFFF" : theme.live
                        }
                    }
                    background: Rectangle {
                        color: startBtn.enabled
                               ? (startBtn.hovered ? "#FF4557" : theme.live)
                               : Qt.alpha(theme.live, 0.12)
                        border.color: startBtn.enabled
                                      ? (startBtn.visualFocus ? "#FFFFFF" : "transparent")
                                      : Qt.alpha(theme.live, 0.45)
                        border.width: 1
                        radius: 6
                        Behavior on color { ColorAnimation { duration: 120 } }
                    }

                    onClicked: {
                        leftTextArea.text = "Préparation du plateau…"
                        rightTextArea.text = "Préparation du plateau…"
                        moderatorTextArea.text = "Direct dans 3, 2, 1…"
                        backstageArea.text = "Coulisses activées."
                        agent1Round = 0
                        agent2Round = 0
                        moderatorRound = 0
                        currentSpeaker = ""
                        audienceQuestionWasRead = false
                        leftFeedPristine = true
                        rightFeedPristine = true
                        modFeedPristine = true

                        var finalTopic = topicInput.text || generatedTheme || (backend ? backend.getDefaultTopic() : "Devons-nous faire confiance à l'IA?")

                        backend.startDebate(finalTopic, selectedDomain)
                    }
                }

                Button {
                    id: stopBtn
                    Layout.preferredHeight: 40
                    enabled: debateRunning
                    text: "COUPER L'ANTENNE"

                    contentItem: Text {
                        text: stopBtn.text
                        font.family: theme.display
                        font.pixelSize: 13
                        font.weight: Font.DemiBold
                        font.letterSpacing: 1.8
                        color: stopBtn.enabled ? theme.ink : theme.inkFaint
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                        leftPadding: 18
                        rightPadding: 18
                    }
                    background: Rectangle {
                        color: stopBtn.enabled && stopBtn.hovered ? theme.panelSoft : "transparent"
                        border.color: stopBtn.enabled
                                      ? (stopBtn.visualFocus ? theme.ink : theme.inkDim)
                                      : theme.lineSoft
                        border.width: 1
                        radius: 6
                        Behavior on color { ColorAnimation { duration: 120 } }
                    }

                    onClicked: backend.stopDebate()
                }
            }
        }
    }

    // ------------------------------------------------------------------
    // Helpers
    // ------------------------------------------------------------------
    function refreshGuestNames() {
        if (!backend)
            return
        var names = backend.getGuestNames(selectedDomain)
        leftGuestName = names.left
        rightGuestName = names.right
    }

    function syncAudienceQueueDepth() {
        if (!backend)
            return
        if (typeof backend.getEarpieceQueueDepth === "function")
            audienceQueueDepth = backend.getEarpieceQueueDepth()
        if (typeof backend.getEarpieceQueueCapacity === "function")
            audienceQueueCapacity = backend.getEarpieceQueueCapacity()
    }

    Component.onCompleted: {
        refreshGuestNames()
        syncAudienceQueueDepth()
    }

    // ------------------------------------------------------------------
    // Backend connections
    // ------------------------------------------------------------------
    Connections {
        target: backend

        function onThemeGenerated(theme) {
            generatedTheme = theme
            topicInput.text = theme
        }

        function onMessageStreamReceived(agentType, content, roundNum) {
            currentSpeaker = agentType
            if (agentType === "moderator" && audienceQuestionWasRead)
                audienceQuestionWasRead = false
            if (agentType === "agent_one") {
                if (leftFeedPristine) {
                    leftTextArea.text = ""
                    leftFeedPristine = false
                }
                if (roundNum > agent1Round) {
                    if (agent1Round > 0) leftTextArea.text += "\n\n"
                    leftTextArea.text += "— MANCHE " + roundNum + " —\n"
                    agent1Round = roundNum
                }
                leftTextArea.text += content
            } else if (agentType === "agent_two") {
                if (rightFeedPristine) {
                    rightTextArea.text = ""
                    rightFeedPristine = false
                }
                if (roundNum > agent2Round) {
                    if (agent2Round > 0) rightTextArea.text += "\n\n"
                    rightTextArea.text += "— MANCHE " + roundNum + " —\n"
                    agent2Round = roundNum
                }
                rightTextArea.text += content
            } else if (agentType === "moderator") {
                if (modFeedPristine) {
                    moderatorTextArea.text = ""
                    modFeedPristine = false
                }
                if (roundNum > moderatorRound) {
                    if (moderatorRound > 0) moderatorTextArea.text += "\n\n"
                    if (roundNum > 0) moderatorTextArea.text += "— INTERVENTION " + roundNum + " —\n"
                    moderatorRound = roundNum
                }
                moderatorTextArea.text += content
            }
        }

        function onBackstageUpdate(content) {
            backstageArea.text += "\n" + content + "\n"
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

        function onAudienceQuestionQueued(question) {
            // Signal : question acceptée en file oreillette (pas encore lue antenne).
            audienceQuestionPending = question
            audienceHint = ""
            syncAudienceQueueDepth()
        }

        function onAudienceQuestionRead(question) {
            // Signal : modérateur a drainé / lit la question à l'antenne.
            audienceQuestionPending = ""
            audienceQuestionWasRead = true
            audienceHint = ""
            syncAudienceQueueDepth()
        }

        function onDebateStatusChanged(isRunning) {
            debateRunning = isRunning
            if (!isRunning) {
                currentSpeaker = ""
                audienceQuestionWasRead = false
            }
            syncAudienceQueueDepth()
        }

        function onDebateFinished() {
            currentSpeaker = ""
            var separator = "──────────────────────"
            leftTextArea.text += "\n\n" + separator + "\nFIN DE L'ÉMISSION\n" + separator
            rightTextArea.text += "\n\n" + separator + "\nFIN DE L'ÉMISSION\n" + separator
            moderatorTextArea.text += "\n\n" + separator + "\nMerci de nous avoir suivis.\n" + separator
            backstageArea.text += "\nÉmission terminée."
        }

        function onErrorOccurred(error) {
            currentSpeaker = ""
            leftTextArea.text += "\n\nErreur : " + error
            rightTextArea.text += "\n\nErreur : " + error
            moderatorTextArea.text += "\n\nErreur technique : " + error
        }
    }
}
