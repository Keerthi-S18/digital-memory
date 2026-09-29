import time
import pygetwindow as gw


def get_active_window():
    window = gw.getActiveWindow()

    if window is None:
        return None

    title = window.title.strip()

    if not title:
        return None

    return title


def monitor():
    previous_window = None

    print("Digital Memory - Windows Collector")
    print("Monitoring active window...")
    print("Press Ctrl+C to stop.\n")

    while True:
        current_window = get_active_window()

        if current_window != previous_window:
            print(f"Window changed: {current_window}")
            previous_window = current_window

        time.sleep(1)


if __name__ == "__main__":
    monitor()