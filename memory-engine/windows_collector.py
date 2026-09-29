import json
import time
from datetime import datetime

import pygetwindow as gw

from memory_store import (
    initialize_database,
    save_event,
    create_session,
    close_session,
    close_open_sessions,
    increment_session_event_count,
)

from context_engine import build_contexts


def get_active_window():
    window = gw.getActiveWindow()

    if window is None:
        return None

    title = window.title.strip()

    if not title:
        return None

    return title


def create_event(window_title):
    parts = window_title.split(" - ")

    if len(parts) > 1:
        application = parts[-1]
        title = " - ".join(parts[:-1])
    else:
        application = window_title
        title = ""

    return {
        "timestamp": datetime.now().isoformat(),
        "source": "windows",
        "event_type": "active_window_changed",
        "details": {
            "application": application,
            "window_title": window_title,
            "title": title
        }
    }


def monitor():
    initialize_database()

    startup_time = datetime.now().isoformat()

    # Recover sessions that were left open by a previous
    # interrupted collector run.
    close_open_sessions(startup_time)

    previous_window = None
    current_session_id = None

    print("Digital Memory - Windows Collector")
    print("Monitoring active window...")
    print("Events, sessions, and contexts are being saved.")
    print("Press Ctrl+C to stop.\n")

    try:
        while True:
            current_window = get_active_window()

            if current_window and current_window != previous_window:
                event = create_event(current_window)

                application = event["details"]["application"]
                title = event["details"]["title"]
                timestamp = event["timestamp"]

                if current_session_id is not None:
                    close_session(
                        session_id=current_session_id,
                        end_time=timestamp,
                    )

                current_session_id = create_session(
                    start_time=timestamp,
                    application=application,
                    title=title,
                )

                save_event(
                    timestamp=timestamp,
                    source=event["source"],
                    event_type=event["event_type"],
                    details=json.dumps(event["details"]),
                    session_id=current_session_id,
                )

                increment_session_event_count(
                    session_id=current_session_id
                )

                build_contexts()

                print(
                    f"Saved: {application} | {title}"
                )

                print(
                    f"Session created: {current_session_id}"
                )

                print("Contexts rebuilt.")

                previous_window = current_window

            time.sleep(1)

    except KeyboardInterrupt:
        print("\nStopping collector...")

        end_time = datetime.now().isoformat()

        if current_session_id is not None:
            close_session(
                session_id=current_session_id,
                end_time=end_time,
            )

        # Safety recovery: close any other session that
        # may still be open.
        close_open_sessions(end_time)

        build_contexts()

        print("Collector stopped safely.")


if __name__ == "__main__":
    monitor()