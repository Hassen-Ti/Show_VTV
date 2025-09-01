import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Layouts

ApplicationWindow {
    id: mainWindow
    visible: true
    width: 1000
    height: 600
    title: "Demo Mini-Ecrans avec VRAIES Screenshots"
    color: "#001122"

    property bool leftScreenVisible: false
    property bool rightScreenVisible: false

    Rectangle {
        anchors.fill: parent
        gradient: Gradient {
            GradientStop { position: 0.0; color: "#001122" }
            GradientStop { position: 1.0; color: "#002244" }
        }
    }

    Text {
        anchors.horizontalCenter: parent.horizontalCenter
        y: 20
        text: "📺 DEMO AVEC VRAIES MINIATURES WEB"
        font.pixelSize: 24
        font.bold: true
        color: "#00ffff"
    }

    RowLayout {
        anchors.fill: parent
        anchors.margins: 60
        anchors.topMargin: 80
        spacing: 20

        // Agent Gauche
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: "transparent"
            border.color: "#00aaff"
            border.width: 2
            radius: 10

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 20
                spacing: 15

                Rectangle {
                    Layout.alignment: Qt.AlignHCenter
                    width: 80
                    height: 80
                    radius: 40
                    color: "#00aaff"
                    
                    Text {
                        anchors.centerIn: parent
                        text: "🔥"
                        font.pixelSize: 40
                    }
                }

                Text {
                    Layout.fillWidth: true
                    text: "AGENT OPTIMISTE"
                    color: "#00aaff"
                    font.bold: true
                    font.pixelSize: 16
                    horizontalAlignment: Text.AlignHCenter
                }

                Rectangle {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    color: Qt.rgba(0, 0.4, 0.8, 0.1)
                    radius: 8
                    border.color: "#00aaff"
                    border.width: 1

                    Text {
                        id: leftAgentText
                        anchors.fill: parent
                        anchors.margins: 15
                        text: "Cliquez pour voir les VRAIES miniatures web!"
                        color: "#ffffff"
                        font.pixelSize: 14
                        wrapMode: Text.Wrap
                        verticalAlignment: Text.AlignVCenter
                    }
                }
            }
        }

        // Centre avec bouton
        Rectangle {
            Layout.preferredWidth: 200
            Layout.fillHeight: true
            color: "transparent"

            ColumnLayout {
                anchors.centerIn: parent
                spacing: 20

                Button {
                    text: "🌐 Demo Vraies\nMiniatures"
                    font.pixelSize: 14
                    font.bold: true
                    palette.buttonText: "#ffcc00"
                    
                    background: Rectangle {
                        color: parent.hovered ? "#443300" : "#221100"
                        border.color: "#ffcc00"
                        border.width: 2
                        radius: 8
                    }
                    
                    onClicked: {
                        demoController.startDemo()
                    }
                }

                Text {
                    text: "VS"
                    color: "#ffcc00"
                    font.bold: true
                    font.pixelSize: 30
                }

                Text {
                    text: "Screenshots\nvia API"
                    color: "#888888"
                    font.pixelSize: 12
                    horizontalAlignment: Text.AlignHCenter
                }
            }
        }

        // Agent Droite
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: "transparent"
            border.color: "#ff4444"
            border.width: 2
            radius: 10

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 20
                spacing: 15

                Rectangle {
                    Layout.alignment: Qt.AlignHCenter
                    width: 80
                    height: 80
                    radius: 40
                    color: "#ff4444"
                    
                    Text {
                        anchors.centerIn: parent
                        text: "💀"
                        font.pixelSize: 40
                    }
                }

                Text {
                    Layout.fillWidth: true
                    text: "AGENT SCEPTIQUE"
                    color: "#ff4444"
                    font.bold: true
                    font.pixelSize: 16
                    horizontalAlignment: Text.AlignHCenter
                }

                Rectangle {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    color: Qt.rgba(0.8, 0.2, 0.2, 0.1)
                    radius: 8
                    border.color: "#ff4444"
                    border.width: 1

                    Text {
                        id: rightAgentText
                        anchors.fill: parent
                        anchors.margins: 15
                        text: "En attente des captures web..."
                        color: "#ffffff"
                        font.pixelSize: 14
                        wrapMode: Text.Wrap
                        verticalAlignment: Text.AlignVCenter
                    }
                }
            }
        }
    }

    // Mini-Ecran Gauche AVEC VRAIE IMAGE
    Rectangle {
        id: leftMiniScreen
        width: 320
        height: 240
        x: leftScreenVisible ? 20 : -width
        y: 120
        color: "#333333"
        border.color: "#00aaff"
        border.width: 3
        radius: 8
        opacity: leftScreenVisible ? 0.95 : 0
        
        Behavior on x {
            NumberAnimation { duration: 600; easing.type: Easing.OutCubic }
        }
        
        Behavior on opacity {
            NumberAnimation { duration: 400 }
        }

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 10
            spacing: 8

            Text {
                text: "📄 MINI-ECRAN GAUCHE"
                color: "#00aaff"
                font.bold: true
                font.pixelSize: 12
                Layout.alignment: Qt.AlignHCenter
            }

            // ZONE POUR LA VRAIE IMAGE
            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 140
                color: "#222222"
                border.color: "#555555"
                border.width: 1
                radius: 4

                Image {
                    id: leftScreenImage
                    anchors.fill: parent
                    anchors.margins: 2
                    fillMode: Image.PreserveAspectFit
                    source: ""  // Sera rempli par Python
                    
                    Rectangle {
                        anchors.fill: parent
                        color: "#444444"
                        visible: leftScreenImage.status !== Image.Ready
                        
                        Text {
                            anchors.centerIn: parent
                            text: leftScreenImage.status === Image.Loading ? "🔄 Chargement..." : "📸 Screenshot"
                            color: "#cccccc"
                            font.pixelSize: 12
                        }
                    }
                }
            }

            Text {
                id: leftScreenTitle
                Layout.fillWidth: true
                text: "Titre..."
                color: "#ffffff"
                font.pixelSize: 11
                font.bold: true
                wrapMode: Text.Wrap
                maximumLineCount: 2
                elide: Text.ElideRight
            }

            Text {
                id: leftScreenUrl
                Layout.fillWidth: true
                text: "url..."
                color: "#aaaaaa"
                font.pixelSize: 9
                elide: Text.ElideMiddle
            }
        }
    }

    // Mini-Ecran Droite AVEC VRAIE IMAGE
    Rectangle {
        id: rightMiniScreen
        width: 320
        height: 240
        x: rightScreenVisible ? parent.width - width - 20 : parent.width
        y: 120
        color: "#333333"
        border.color: "#ff4444"
        border.width: 3
        radius: 8
        opacity: rightScreenVisible ? 0.95 : 0
        
        Behavior on x {
            NumberAnimation { duration: 600; easing.type: Easing.OutCubic }
        }
        
        Behavior on opacity {
            NumberAnimation { duration: 400 }
        }

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 10
            spacing: 8

            Text {
                text: "📄 MINI-ECRAN DROITE"
                color: "#ff4444"
                font.bold: true
                font.pixelSize: 12
                Layout.alignment: Qt.AlignHCenter
            }

            // ZONE POUR LA VRAIE IMAGE
            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 140
                color: "#222222"
                border.color: "#555555"
                border.width: 1
                radius: 4

                Image {
                    id: rightScreenImage
                    anchors.fill: parent
                    anchors.margins: 2
                    fillMode: Image.PreserveAspectFit
                    source: ""  // Sera rempli par Python
                    
                    Rectangle {
                        anchors.fill: parent
                        color: "#444444"
                        visible: rightScreenImage.status !== Image.Ready
                        
                        Text {
                            anchors.centerIn: parent
                            text: rightScreenImage.status === Image.Loading ? "🔄 Chargement..." : "📸 Screenshot"
                            color: "#cccccc"
                            font.pixelSize: 12
                        }
                    }
                }
            }

            Text {
                id: rightScreenTitle
                Layout.fillWidth: true
                text: "Titre..."
                color: "#ffffff"
                font.pixelSize: 11
                font.bold: true
                wrapMode: Text.Wrap
                maximumLineCount: 2
                elide: Text.ElideRight
            }

            Text {
                id: rightScreenUrl
                Layout.fillWidth: true
                text: "url..."
                color: "#aaaaaa"
                font.pixelSize: 9
                elide: Text.ElideMiddle
            }
        }
    }

    Connections {
        target: demoController

        function onShowMiniScreen(position, title, url, screenshotUrl) {
            if (position === "left") {
                leftScreenVisible = true
                leftScreenTitle.text = title
                leftScreenUrl.text = url
                leftScreenImage.source = screenshotUrl  // VRAIE IMAGE!
            } else if (position === "right") {
                rightScreenVisible = true
                rightScreenTitle.text = title
                rightScreenUrl.text = url
                rightScreenImage.source = screenshotUrl  // VRAIE IMAGE!
            }
        }

        function onShowLoadingScreen(position, title, url) {
            // Affiche loading pendant capture
            if (position === "left") {
                leftScreenVisible = true
                leftScreenTitle.text = title
                leftScreenUrl.text = url
                leftScreenImage.source = ""  // Pas d'image = loading
            } else if (position === "right") {
                rightScreenVisible = true
                rightScreenTitle.text = title
                rightScreenUrl.text = url
                rightScreenImage.source = ""  // Pas d'image = loading
            }
        }

        function onHideMiniScreen(position) {
            if (position === "left") {
                leftScreenVisible = false
            } else if (position === "right") {
                rightScreenVisible = false
            }
        }

        function onUpdateAgentText(agent, text) {
            if (agent === "left") {
                leftAgentText.text = text
            } else if (agent === "right") {
                rightAgentText.text = text
            }
        }
    }
}