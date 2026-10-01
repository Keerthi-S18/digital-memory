import json
from datetime import datetime

from memory_store import (
    initialize_database,
    get_events,
    get_events_between,
    get_sessions,
    get_session_events,
    get_contexts,
    get_context_sessions,
)


def print_header(title):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def format_event(event):
    event_id, timestamp, source, event_type, details, session_id = event

    try:
        details_data = json.loads(details)
    except (json.JSONDecodeError, TypeError):
        details_data = {"raw": details}

    return {
        "id": event_id,
        "timestamp": timestamp,
        "application": details_data.get("application", source),
        "title": details_data.get("title", ""),
        "window_title": details_data.get("window_title", ""),
        "event_type": event_type,
        "session_id": session_id,
    }


def print_timeline(events):
    if not events:
        print("\nNo events found.")
        return

    for event in events:
        item = format_event(event)

        print(
            f"{item['timestamp']} | "
            f"{item['application']} | "
            f"{item['title']}"
        )


def show_timeline():
    print_header("DIGITAL MEMORY - TIMELINE")
    print_timeline(get_events())


def search_events():
    print_header("DIGITAL MEMORY - SEARCH")

    query = input("Search for: ").strip().lower()

    if not query:
        print("Search cancelled.")
        return

    matches = []

    for event in get_events():
        item = format_event(event)

        searchable = " ".join(
            [
                item["application"],
                item["title"],
                item["window_title"],
                item["event_type"],
            ]
        ).lower()

        if query in searchable:
            matches.append(event)

    if not matches:
        print("\nNo matching memory found.")
        return

    print(f"\nFound {len(matches)} matching event(s):\n")
    print_timeline(matches)


def parse_datetime(value):
    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(value.strip(), fmt)
        except ValueError:
            pass

    return None


def show_time_range():
    print_header("DIGITAL MEMORY - TIME RANGE")
    print("Use format: YYYY-MM-DD HH:MM\n")

    start = parse_datetime(input("Start: "))
    end = parse_datetime(input("End: "))

    if start is None or end is None:
        print("\nInvalid date/time format.")
        return

    events = get_events_between(
        start.isoformat(),
        end.isoformat(),
    )

    print()

    if not events:
        print("No memory found in this time range.")
        return

    print_timeline(events)


def show_sessions():
    print_header("DIGITAL MEMORY - SESSIONS")

    sessions = get_sessions()

    if not sessions:
        print("\nNo sessions found.")
        return

    for session in sessions:
        (
            session_id,
            start_time,
            end_time,
            application,
            title,
            event_count,
        ) = session

        print(f"\nSession {session_id}")
        print(f"Application : {application}")
        print(f"Title       : {title}")
        print(f"Start       : {start_time}")
        print(f"End         : {end_time}")
        print(f"Events      : {event_count}")


def show_session_details():
    print_header("DIGITAL MEMORY - SESSION DETAILS")

    try:
        session_id = int(input("Session ID: ").strip())
    except ValueError:
        print("\nInvalid session ID.")
        return

    events = get_session_events(session_id)

    if not events:
        print("\nNo events found for that session.")
        return

    print(f"\nEvents in session {session_id}:\n")
    print_timeline(events)


def show_contexts():
    print_header("DIGITAL MEMORY - CONTEXTS")

    contexts = get_contexts()

    if not contexts:
        print("\nNo contexts found.")
        return

    for context in contexts:
        (
            context_id,
            start_time,
            end_time,
            name,
            session_count,
            summary,
        ) = context

        print(f"\nContext {context_id}")
        print(f"Name     : {name}")
        print(f"Start    : {start_time}")
        print(f"End      : {end_time}")
        print(f"Sessions : {session_count}")
        print(f"Summary  : {summary}")

        sessions = get_context_sessions(context_id)

        if sessions:
            print("Activity:")

            for session in sessions:
                (
                    session_id,
                    session_start,
                    session_end,
                    application,
                    title,
                    event_count,
                ) = session

                print(f"  - {application}: {title}")


def is_coding_activity(application, title):
    text = f"{application} {title}".lower()

    signals = [
        "vs code",
        "visual studio code",
        "pycharm",
        "intellij",
        "android studio",
        "terminal",
        "powershell",
        "command prompt",
        ".py",
        ".js",
        ".ts",
        ".java",
        ".cpp",
        ".c",
        ".cs",
        ".html",
        ".css",
        ".sql",
    ]

    return any(signal in text for signal in signals)


def is_research_activity(application, title):
    text = f"{application} {title}".lower()

    signals = [
        "chrome",
        "edge",
        "firefox",
        "google",
        "search",
        "github",
        "stackoverflow",
        "documentation",
        "docs",
        "wikipedia",
    ]

    return any(signal in text for signal in signals)


def get_context_activity(context_id):
    activities = []

    for session in get_context_sessions(context_id):
        (
            session_id,
            start_time,
            end_time,
            application,
            title,
            event_count,
        ) = session

        activities.append(
            {
                "session_id": session_id,
                "start_time": start_time,
                "end_time": end_time,
                "application": application,
                "title": title,
            }
        )

    return activities


def question_type(question):
    question = question.lower()

    if any(
        phrase in question
        for phrase in [
            "what was i researching",
            "what did i research",
            "what was i looking up",
            "what was i searching",
        ]
    ):
        return "research"

    if any(
        phrase in question
        for phrase in [
            "what was i coding",
            "what was i programming",
            "what code was i working on",
            "what was i developing",
        ]
    ):
        return "coding"

    if any(
        phrase in question
        for phrase in [
            "what was i working on",
            "what did i do",
            "what was i doing",
            "what happened earlier",
        ]
    ):
        return "general"

    return "general"


def ask_memory():
    print_header("DIGITAL MEMORY - ASK MEMORY")

    question = input("Ask your memory: ").strip()

    if not question:
        print("Question cancelled.")
        return

    contexts = get_contexts()

    if not contexts:
        print("\nI don't have enough memory yet.")
        return

    kind = question_type(question)

    matches = []

    for context in contexts:
        activities = get_context_activity(context[0])

        coding_count = sum(
            1
            for activity in activities
            if is_coding_activity(
                activity["application"],
                activity["title"],
            )
        )

        research_count = sum(
            1
            for activity in activities
            if is_research_activity(
                activity["application"],
                activity["title"],
            )
        )

        if kind == "coding":
            score = coding_count * 5

        elif kind == "research":
            score = research_count * 5

        else:
            score = (
                coding_count
                + research_count
                + 1
            )

        if score > 0:
            matches.append(
                (
                    score,
                    context,
                    activities,
                )
            )

    matches.sort(
        key=lambda item: (
            item[0],
            item[1][1],
        ),
        reverse=True,
    )

    if not matches:
        print("\nI couldn't find a relevant memory.")
        return

    print("\nDIGITAL MEMORY - ANSWER\n")

    if kind == "research":
        print("You were researching:")

    elif kind == "coding":
        print("You were working on coding/development:")

    else:
        print("You were working on:")

    shown_activities = set()

    for score, context, activities in matches[:3]:
        (
            context_id,
            start_time,
            end_time,
            name,
            session_count,
            summary,
        ) = context

        relevant = []

        for activity in activities:
            key = (
                activity["application"],
                activity["title"],
            )

            if key in shown_activities:
                continue

            if kind == "research":
                if is_research_activity(
                    activity["application"],
                    activity["title"],
                ):
                    relevant.append(activity)

            elif kind == "coding":
                if is_coding_activity(
                    activity["application"],
                    activity["title"],
                ):
                    relevant.append(activity)

            else:
                relevant.append(activity)

        if not relevant:
            continue

        print(f"\nContext : {name}")
        print(f"Start   : {start_time}")
        print(f"End     : {end_time}")

        print("Activity:")

        for activity in relevant:
            key = (
                activity["application"],
                activity["title"],
            )

            shown_activities.add(key)

            print(
                f"  - {activity['application']}: "
                f"{activity['title']}"
            )


def main():
    initialize_database()

    while True:
        print_header("DIGITAL MEMORY")

        print("1. Timeline")
        print("2. Search")
        print("3. Time Range")
        print("4. Sessions")
        print("5. Session Details")
        print("6. Contexts")
        print("7. Ask Memory")
        print("0. Exit")

        choice = input("\nChoose an option: ").strip()

        if choice == "1":
            show_timeline()

        elif choice == "2":
            search_events()

        elif choice == "3":
            show_time_range()

        elif choice == "4":
            show_sessions()

        elif choice == "5":
            show_session_details()

        elif choice == "6":
            show_contexts()

        elif choice == "7":
            ask_memory()

        elif choice == "0":
            print("\nGoodbye.")
            break

        else:
            print("\nInvalid option.")

        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()