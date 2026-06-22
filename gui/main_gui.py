import os
import sys
from PySide6.QtCore import QObject, Slot, Signal, QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

import shutdown_core
import csv
from datetime import datetime


class Backend(QObject):
    notify = Signal(str)
    scheduleChanged = Signal(str, int, bool)
    statsChanged = Signal()

    def __init__(self):
        super().__init__()

    @Slot(int, int, bool)
    def schedule(self, hour, minute, testMode):
        def on_scheduled(seconds, target_time):
            self.scheduleChanged.emit(target_time, seconds, testMode)
            self.notify.emit(f"Scheduled for {target_time}")

        def on_performed(kind):
            self.notify.emit(f"Performed: {kind}")
            self.statsChanged.emit()

        try:
            shutdown_core.schedule_shutdown_at(hour, minute, testMode, on_scheduled=on_scheduled, on_performed=on_performed)
            self.statsChanged.emit()
        except ValueError as exc:
            self.notify.emit(str(exc))

    @Slot()
    def cancel(self):
        ok = shutdown_core.cancel_shutdown()
        self.notify.emit("Cancel requested" if ok else "Cancel failed")
        if ok:
            self.scheduleChanged.emit("--:--", 0, True)
        self.statsChanged.emit()

    @Slot(result='QVariant')
    def getStats(self):
        stats = shutdown_core.get_stats(50)
        for item in stats:
            seconds = item.get("scheduled_seconds") or 0
            item["duration"] = self._format_duration(seconds)
            item["mode"] = "Test" if item.get("event_type") == "scheduled_test" else "Shutdown"
            item["state"] = "Done" if item.get("performed") else "Pending"
            ts = item.get("ts") or ""
            item["display_ts"] = ts.replace("T", " ")[:16]
        return stats

    @staticmethod
    def _format_duration(seconds):
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        if hours and minutes:
            return f"{hours}h {minutes}m"
        if hours:
            return f"{hours}h"
        return f"{minutes}m"

    @Slot(result=str)
    def exportStats(self):
        """Export recent stats to a timestamped CSV file and return the path."""
        items = shutdown_core.get_stats(100)
        folder = os.path.dirname(__file__)
        fname = f"shutdown_stats_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
        path = os.path.join(folder, fname)
        try:
            with open(path, "w", newline='', encoding='utf-8') as f:
                w = csv.writer(f)
                w.writerow(["id", "ts", "event_type", "scheduled_seconds", "performed"])
                for it in items:
                    w.writerow([it.get("id"), it.get("ts"), it.get("event_type"), it.get("scheduled_seconds"), int(it.get("performed"))])
            self.notify.emit(f"Exported stats to: {path}")
            return path
        except Exception as e:
            self.notify.emit(f"Export failed: {e}")
            return ""


def run_qt_ui():
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()

    backend = Backend()
    ctxt = engine.rootContext()
    ctxt.setContextProperty("backend", backend)

    qml_path = os.path.join(os.path.dirname(__file__), "main.qml")
    engine.load(QUrl.fromLocalFile(qml_path))

    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec())


if __name__ == "__main__":
    run_qt_ui()
