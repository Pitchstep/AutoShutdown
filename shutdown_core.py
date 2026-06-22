import os
import sys
import time
import threading
import sqlite3
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "autoshutdown_stats.db")
_active_timer_cancel = None
_active_timer_lock = threading.Lock()


def _get_db_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    return conn


def init_db():
    conn = _get_db_conn()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT,
            event_type TEXT,
            scheduled_seconds INTEGER,
            performed INTEGER
        )
        """
    )
    conn.commit()
    conn.close()


def version():
    return "1.00"


def _insert_event(event_type, scheduled_seconds):
    conn = _get_db_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO events (ts, event_type, scheduled_seconds, performed) VALUES (?, ?, ?, ?)",
        (datetime.utcnow().isoformat(), event_type, scheduled_seconds, 0),
    )
    eid = cur.lastrowid
    conn.commit()
    conn.close()
    return eid


def _mark_event_performed(eid):
    conn = _get_db_conn()
    cur = conn.cursor()
    cur.execute("UPDATE events SET performed = 1 WHERE id = ?", (eid,))
    conn.commit()
    conn.close()


def get_stats(limit=100):
    conn = _get_db_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, ts, event_type, scheduled_seconds, performed FROM events ORDER BY id DESC LIMIT ?", (limit,))
    rows = cur.fetchall()
    conn.close()
    stats = []
    for r in rows:
        stats.append({
            "id": r[0],
            "ts": r[1],
            "event_type": r[2],
            "scheduled_seconds": r[3],
            "performed": bool(r[4]),
        })
    return stats


def _format_target_time(seconds_to_wait):
    target = time.localtime(time.time() + seconds_to_wait)
    return time.strftime("%H:%M", target)


def schedule_shutdown_at(hour: int, minute: int, test_mode: bool, on_scheduled=None, on_performed=None):
    global _active_timer_cancel

    if not 0 <= hour <= 23:
        raise ValueError("hour must be between 0 and 23")
    if not 0 <= minute <= 59:
        raise ValueError("minute must be between 0 and 59")

    now = time.localtime()
    current_hour, current_minute, current_second = now.tm_hour, now.tm_min, now.tm_sec

    target_seconds = hour * 3600 + minute * 60
    current_seconds = current_hour * 3600 + current_minute * 60 + current_second

    if target_seconds <= current_seconds:
        seconds_to_wait = 86400 - current_seconds + target_seconds  # next day
    else:
        seconds_to_wait = target_seconds - current_seconds

    target_time = _format_target_time(seconds_to_wait)
    cancel_event = threading.Event()

    with _active_timer_lock:
        if _active_timer_cancel is not None:
            _active_timer_cancel.set()
        _active_timer_cancel = cancel_event

    eid = _insert_event("scheduled_test" if test_mode else "scheduled_shutdown", seconds_to_wait)

    if callable(on_scheduled):
        try:
            on_scheduled(seconds_to_wait, target_time)
        except Exception:
            pass

    def _wait_and_act(secs, test, record_id, cancel_token):
        global _active_timer_cancel

        if cancel_token.wait(secs):
            return

        if test:
            _mark_event_performed(record_id)
            if callable(on_performed):
                on_performed("test")
        else:
            try:
                if os.name == "nt":
                    os.system("shutdown /s /t 0")
                elif sys.platform == "darwin":
                    os.system("osascript -e 'tell application \"System Events\" to shut down'")
                else:
                    os.system("shutdown -h now")
                _mark_event_performed(record_id)
                if callable(on_performed):
                    on_performed("shutdown")
            except Exception:
                if callable(on_performed):
                    on_performed("error")

        with _active_timer_lock:
            if _active_timer_cancel is cancel_token:
                _active_timer_cancel = None

    threading.Thread(target=_wait_and_act, args=(seconds_to_wait, test_mode, eid, cancel_event), daemon=True).start()
    return {
        "seconds_to_wait": seconds_to_wait,
        "target_time": target_time,
        "test_mode": test_mode,
    }


def cancel_shutdown():
    global _active_timer_cancel

    canceled_in_app_timer = False
    with _active_timer_lock:
        if _active_timer_cancel is not None:
            _active_timer_cancel.set()
            _active_timer_cancel = None
            canceled_in_app_timer = True

    try:
        if os.name == "nt":
            os.system("shutdown /a")
        else:
            # no portable cancel; best-effort
            os.system("killall shutdown || true")
        return True or canceled_in_app_timer
    except Exception:
        return canceled_in_app_timer


# initialize DB on import
init_db()
