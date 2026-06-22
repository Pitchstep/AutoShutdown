import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

ApplicationWindow {
    id: window
    visible: true
    width: 760
    height: 560
    minimumWidth: 620
    minimumHeight: 500
    title: "AutoShutdown"
    color: "#111827"

    property int currentPage: 0
    property string scheduledTime: "--:--"
    property int scheduledSeconds: 0
    property bool scheduledTestMode: true
    property string noticeText: "Ready"
    property bool isBusy: false
    property string busyText: "Working..."

    function durationText(seconds) {
        var hours = Math.floor(seconds / 3600)
        var minutes = Math.floor((seconds % 3600) / 60)
        if (hours > 0 && minutes > 0) return hours + "h " + minutes + "m"
        if (hours > 0) return hours + "h"
        return minutes + "m"
    }

    function beginBusy(message) {
        busyText = message
        isBusy = true
    }

    function endBusy() {
        isBusy = false
    }

    function reloadStats() {
        beginBusy("Loading history...")
        loadStatsTimer.restart()
    }

    function applyStats() {
        var items = backend.getStats()
        statsModel.clear()
        for (var i = 0; i < items.length; i++) {
            statsModel.append(items[i])
        }
        chartCanvas.chartData = items.slice(0, Math.min(14, items.length)).reverse()
        chartCanvas.requestPaint()
        endBusy()
    }

    QtObject {
        id: palette
        property color page: "#111827"
        property color panel: "#172033"
        property color panelAlt: "#1f2937"
        property color field: "#0f172a"
        property color line: "#334155"
        property color text: "#f8fafc"
        property color muted: "#94a3b8"
        property color accent: "#2dd4bf"
        property color accentStrong: "#14b8a6"
        property color warning: "#f97316"
        property color danger: "#ef4444"
    }

    background: Rectangle { color: palette.page }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 18
        spacing: 14

        RowLayout {
            Layout.fillWidth: true
            spacing: 14

            ColumnLayout {
                Layout.fillWidth: true
                spacing: 2

                Label {
                    text: "AutoShutdown"
                    color: palette.text
                    font.pixelSize: 28
                    font.bold: true
                }
                Label {
                    text: "Schedule one shutdown timer for this device."
                    color: palette.muted
                    font.pixelSize: 13
                }
            }

            Rectangle {
                Layout.preferredWidth: 280
                Layout.preferredHeight: 48
                radius: 8
                color: palette.panel
                border.width: 1
                border.color: palette.line

                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 4
                    spacing: 4

                    Repeater {
                        model: ["Schedule", "History"]
                        delegate: Button {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            text: modelData
                            checkable: true
                            checked: currentPage === index
                            onClicked: {
                                currentPage = index
                                if (index === 1) reloadStats()
                            }
                            enabled: !isBusy
                            font.pixelSize: 13
                            contentItem: Text {
                                text: parent.text
                                color: parent.checked ? "#031411" : palette.text
                                horizontalAlignment: Text.AlignHCenter
                                verticalAlignment: Text.AlignVCenter
                                font: parent.font
                            }
                            background: Rectangle {
                                radius: 7
                                color: parent.checked ? palette.accent : "transparent"
                            }
                        }
                    }
                }
            }
        }

        StackLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            currentIndex: currentPage

            RowLayout {
                spacing: 14

                Rectangle {
                    Layout.preferredWidth: 310
                    Layout.fillHeight: true
                    radius: 8
                    color: palette.panel
                    border.width: 1
                    border.color: palette.line

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 18
                        spacing: 16

                        Label {
                            text: "Shutdown Time"
                            color: palette.text
                            font.pixelSize: 18
                            font.bold: true
                        }

                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 10

                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: 6
                                Label { text: "Hour"; color: palette.muted; font.pixelSize: 12 }
                                SpinBox {
                                    id: hourBox
                                    from: 0
                                    to: 23
                                    value: 22
                                    editable: true
                                    Layout.fillWidth: true
                                    background: Rectangle { color: palette.field; radius: 8; border.width: 1; border.color: palette.line }
                                    contentItem: TextInput {
                                        text: hourBox.textFromValue(hourBox.value, hourBox.locale)
                                        color: palette.text
                                        horizontalAlignment: Qt.AlignHCenter
                                        verticalAlignment: Qt.AlignVCenter
                                        font.pixelSize: 20
                                        readOnly: !hourBox.editable
                                        validator: hourBox.validator
                                        inputMethodHints: Qt.ImhFormattedNumbersOnly
                                    }
                                }
                            }

                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: 6
                                Label { text: "Minute"; color: palette.muted; font.pixelSize: 12 }
                                SpinBox {
                                    id: minuteBox
                                    from: 0
                                    to: 59
                                    value: 0
                                    editable: true
                                    Layout.fillWidth: true
                                    background: Rectangle { color: palette.field; radius: 8; border.width: 1; border.color: palette.line }
                                    contentItem: TextInput {
                                        text: minuteBox.textFromValue(minuteBox.value, minuteBox.locale)
                                        color: palette.text
                                        horizontalAlignment: Qt.AlignHCenter
                                        verticalAlignment: Qt.AlignVCenter
                                        font.pixelSize: 20
                                        readOnly: !minuteBox.editable
                                        validator: minuteBox.validator
                                        inputMethodHints: Qt.ImhFormattedNumbersOnly
                                    }
                                }
                            }
                        }

                        Rectangle {
                            Layout.fillWidth: true
                            Layout.preferredHeight: 54
                            radius: 8
                            color: palette.field
                            border.width: 1
                            border.color: palette.line

                            RowLayout {
                                anchors.fill: parent
                                anchors.margins: 12
                                Label {
                                    Layout.fillWidth: true
                                    text: "Test mode"
                                    color: palette.text
                                    font.pixelSize: 14
                                }
                                Switch {
                                    id: testMode
                                    checked: true
                                }
                            }
                        }

                        Button {
                            Layout.fillWidth: true
                            Layout.preferredHeight: 44
                            text: "Schedule Shutdown"
                            enabled: !isBusy
                            onClicked: {
                                beginBusy("Scheduling timer...")
                                scheduleTimer.restart()
                            }
                            font.pixelSize: 14
                            font.bold: true
                            contentItem: Text {
                                text: parent.text
                                color: "#041311"
                                horizontalAlignment: Text.AlignHCenter
                                verticalAlignment: Text.AlignVCenter
                                font: parent.font
                            }
                            background: Rectangle {
                                radius: 8
                                color: parent.down ? palette.accentStrong : parent.hovered ? "#22c7b8" : palette.accent
                            }
                        }

                        Button {
                            Layout.fillWidth: true
                            Layout.preferredHeight: 42
                            text: "Cancel Timer"
                            enabled: !isBusy
                            onClicked: {
                                beginBusy("Canceling timer...")
                                cancelTimer.restart()
                            }
                            font.pixelSize: 14
                            contentItem: Text {
                                text: parent.text
                                color: palette.text
                                horizontalAlignment: Text.AlignHCenter
                                verticalAlignment: Text.AlignVCenter
                                font: parent.font
                            }
                            background: Rectangle {
                                radius: 8
                                color: parent.down ? "#b91c1c" : parent.hovered ? "#dc2626" : palette.danger
                            }
                        }

                        Item { Layout.fillHeight: true }
                    }
                }

                ColumnLayout {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    spacing: 14

                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 210
                        radius: 8
                        color: palette.panel
                        border.width: 1
                        border.color: palette.line

                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: 18
                            spacing: 12

                            Label {
                                text: "Current Timer"
                                color: palette.muted
                                font.pixelSize: 12
                            }

                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 16

                                Label {
                                    text: scheduledTime
                                    color: palette.text
                                    font.pixelSize: 56
                                    font.bold: true
                                }
                                ColumnLayout {
                                    Layout.fillWidth: true
                                    spacing: 6
                                    Label {
                                        text: scheduledSeconds > 0 ? durationText(scheduledSeconds) + " remaining" : "No active timer"
                                        color: palette.text
                                        font.pixelSize: 18
                                        font.bold: true
                                    }
                                    Label {
                                        text: scheduledSeconds > 0 ? (scheduledTestMode ? "Test mode: no shutdown will run." : "Live shutdown is armed.") : "Choose a time and schedule when ready."
                                        color: scheduledSeconds > 0 && !scheduledTestMode ? palette.warning : palette.muted
                                        font.pixelSize: 13
                                        wrapMode: Text.WordWrap
                                        Layout.fillWidth: true
                                    }
                                }
                            }

                            Rectangle {
                                Layout.fillWidth: true
                                Layout.preferredHeight: 1
                                color: palette.line
                            }

                            Label {
                                text: noticeText
                                color: palette.accent
                                font.pixelSize: 13
                                elide: Text.ElideRight
                                Layout.fillWidth: true
                            }
                        }
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        radius: 8
                        color: palette.panel
                        border.width: 1
                        border.color: palette.line

                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: 18
                            spacing: 12

                            RowLayout {
                                Layout.fillWidth: true
                                Label {
                                    Layout.fillWidth: true
                                    text: "Recent Activity"
                                    color: palette.text
                                    font.pixelSize: 18
                                    font.bold: true
                                }
                                Button {
                                    text: "Refresh"
                                    enabled: !isBusy
                                    onClicked: reloadStats()
                                    contentItem: Text {
                                        text: parent.text
                                        color: palette.text
                                        horizontalAlignment: Text.AlignHCenter
                                        verticalAlignment: Text.AlignVCenter
                                        font: parent.font
                                    }
                                    background: Rectangle {
                                        radius: 8
                                        color: parent.down ? "#334155" : parent.hovered ? "#2b3748" : palette.panelAlt
                                        border.width: 1
                                        border.color: palette.line
                                    }
                                }
                            }

                            ListView {
                                id: homeStatsView
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                clip: true
                                model: statsModel
                                delegate: Rectangle {
                                    width: homeStatsView.width
                                    height: 42
                                    color: index % 2 === 0 ? "transparent" : "#1c2738"
                                    RowLayout {
                                        anchors.fill: parent
                                        anchors.leftMargin: 10
                                        anchors.rightMargin: 10
                                        spacing: 10
                                        Label { text: mode; color: palette.text; Layout.preferredWidth: 84; elide: Text.ElideRight }
                                        Label { text: duration; color: palette.muted; Layout.preferredWidth: 70 }
                                        Label { text: display_ts; color: palette.muted; Layout.fillWidth: true; elide: Text.ElideRight }
                                        Label { text: state; color: performed ? palette.accent : palette.warning; Layout.preferredWidth: 58; horizontalAlignment: Text.AlignRight }
                                    }
                                }
                            }
                        }
                    }
                }
            }

            ColumnLayout {
                spacing: 14

                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 230
                    radius: 8
                    color: palette.panel
                    border.width: 1
                    border.color: palette.line

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 18
                        spacing: 10

                        RowLayout {
                            Layout.fillWidth: true
                            Label {
                                Layout.fillWidth: true
                                text: "Scheduled Duration History"
                                color: palette.text
                                font.pixelSize: 18
                                font.bold: true
                            }
                            Button {
                                text: "Export CSV"
                                enabled: !isBusy
                                onClicked: {
                                    beginBusy("Exporting CSV...")
                                    exportTimer.restart()
                                }
                                contentItem: Text {
                                    text: parent.text
                                    color: palette.text
                                    horizontalAlignment: Text.AlignHCenter
                                    verticalAlignment: Text.AlignVCenter
                                    font: parent.font
                                }
                                background: Rectangle {
                                    radius: 8
                                    color: parent.down ? "#334155" : parent.hovered ? "#2b3748" : palette.panelAlt
                                    border.width: 1
                                    border.color: palette.line
                                }
                            }
                        }

                        Canvas {
                            id: chartCanvas
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            property var chartData: []
                            onPaint: {
                                var ctx = getContext("2d")
                                ctx.clearRect(0, 0, width, height)
                                ctx.strokeStyle = "#334155"
                                ctx.lineWidth = 1
                                ctx.beginPath()
                                ctx.moveTo(0, height - 24)
                                ctx.lineTo(width, height - 24)
                                ctx.stroke()
                                if (!chartData || chartData.length === 0) return
                                var maxv = 1
                                for (var i = 0; i < chartData.length; i++) {
                                    if (chartData[i].scheduled_seconds > maxv) maxv = chartData[i].scheduled_seconds
                                }
                                var gap = 8
                                var barWidth = Math.max(10, (width - gap * (chartData.length + 1)) / chartData.length)
                                for (var j = 0; j < chartData.length; j++) {
                                    var v = chartData[j].scheduled_seconds
                                    var h = Math.max(2, (v / maxv) * (height - 44))
                                    ctx.fillStyle = chartData[j].performed ? "#2dd4bf" : "#f97316"
                                    ctx.fillRect(gap + j * (barWidth + gap), height - h - 24, barWidth, h)
                                }
                            }
                        }
                    }
                }

                Rectangle {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    radius: 8
                    color: palette.panel
                    border.width: 1
                    border.color: palette.line

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 18
                        spacing: 10

                        RowLayout {
                            Layout.fillWidth: true
                            Label {
                                Layout.fillWidth: true
                                text: "History"
                                color: palette.text
                                font.pixelSize: 18
                                font.bold: true
                            }
                            Button {
                                text: "Refresh"
                                enabled: !isBusy
                                onClicked: reloadStats()
                                contentItem: Text {
                                    text: parent.text
                                    color: palette.text
                                    horizontalAlignment: Text.AlignHCenter
                                    verticalAlignment: Text.AlignVCenter
                                    font: parent.font
                                }
                                background: Rectangle {
                                    radius: 8
                                    color: parent.down ? "#334155" : parent.hovered ? "#2b3748" : palette.panelAlt
                                    border.width: 1
                                    border.color: palette.line
                                }
                            }
                        }

                        ListView {
                            id: statsView
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            clip: true
                            model: statsModel
                            delegate: Rectangle {
                                width: statsView.width
                                height: 44
                                color: index % 2 === 0 ? "transparent" : "#1c2738"
                                RowLayout {
                                    anchors.fill: parent
                                    anchors.leftMargin: 10
                                    anchors.rightMargin: 10
                                    spacing: 10
                                    Label { text: "#" + id; color: palette.muted; Layout.preferredWidth: 50 }
                                    Label { text: mode; color: palette.text; Layout.preferredWidth: 86; elide: Text.ElideRight }
                                    Label { text: duration; color: palette.muted; Layout.preferredWidth: 70 }
                                    Label { text: display_ts; color: palette.muted; Layout.fillWidth: true; elide: Text.ElideRight }
                                    Label { text: state; color: performed ? palette.accent : palette.warning; Layout.preferredWidth: 64; horizontalAlignment: Text.AlignRight }
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    ListModel { id: statsModel }

    Timer {
        id: loadStatsTimer
        interval: 40
        repeat: false
        onTriggered: applyStats()
    }

    Timer {
        id: scheduleTimer
        interval: 40
        repeat: false
        onTriggered: {
            backend.schedule(hourBox.value, minuteBox.value, testMode.checked)
            reloadStats()
        }
    }

    Timer {
        id: cancelTimer
        interval: 40
        repeat: false
        onTriggered: {
            backend.cancel()
            reloadStats()
        }
    }

    Timer {
        id: exportTimer
        interval: 40
        repeat: false
        onTriggered: {
            backend.exportStats()
            endBusy()
        }
    }

    Connections {
        target: backend
        function onNotify(message) {
            noticeText = message
        }
        function onScheduleChanged(targetTime, seconds, testMode) {
            scheduledTime = targetTime
            scheduledSeconds = seconds
            scheduledTestMode = testMode
        }
        function onStatsChanged() {
            reloadStats()
        }
    }

    Component.onCompleted: reloadStats()

    Rectangle {
        anchors.fill: parent
        z: 100
        visible: isBusy
        color: "#990f172a"

        Rectangle {
            width: 260
            height: 118
            radius: 8
            color: palette.panel
            border.width: 1
            border.color: palette.line
            anchors.centerIn: parent

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 18
                spacing: 12

                BusyIndicator {
                    running: isBusy
                    Layout.alignment: Qt.AlignHCenter
                }
                Label {
                    text: busyText
                    color: palette.text
                    font.pixelSize: 14
                    horizontalAlignment: Text.AlignHCenter
                    Layout.fillWidth: true
                }
            }
        }
    }
}
