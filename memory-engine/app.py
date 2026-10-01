import json
from datetime import datetime

from memory_store import (
    initialize_database,
    get_events,
    get_events_between,
    get_sessions,
    get_sessions_between,
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

    application = details_data.get("application", source)
    title = details_data.get("title", "")
    window_title = details_data.get("window_title", "")

    return {
        "id": event_id,
        "timestamp": timestamp,
        "application": application,
        "title": title,
        "window_title": window_title,
        "event_type": event_type,
        "session_id": session_id,
    }


def print_timeline(events):
    if not events:
        print("\nNo events found.")
        return

    for event in events:
        formatted = format_event(event)

        print(
            f"{formatted['timestamp']} | "
            f"{formatted['application']} | "
            f"{formatted['title']}"
        )


def show_timeline():
    print_header("DIGITAL MEMORY - TIMELINE")

    events = get_events()

    print_timeline(events)


def search_events():
    print_header("DIGITAL MEMORY - SEARCH")

    query = input("Search for: ").strip().lower()

    if not query:
        print("Search cancelled.")
        return

    events = get_events()

    matches = []

    for event in events:
        formatted = format_event(event)

        searchable_text = " ".join(
            [
                formatted["application"],
                formatted["title"],
                formatted["window_title"],
                formatted["event_type"],
            ]
        ).lower()

        if query in searchable_text:
            matches.append(event)

    if not matches:
        print("\nNo matching memory found.")
        return

    print(f"\nFound {len(matches)} matching event(s):\n")

    print_timeline(matches)


def parse_datetime(value):
    value = value.strip()

    formats = [
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d %H:%M:%S",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue

    return None


def show_time_range():
    print_header("DIGITAL MEMORY - TIME RANGE")

    print("Use format: YYYY-MM-DD HH:MM")
    print()

    start_input = input("Start: ")
    end_input = input("End: ")

    start = parse_datetime(start_input)
    end = parse_datetime(end_input)

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

    session_input = input("Session ID: ").strip()

    try:
        session_id = int(session_input)
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

                print(
                    f"  - {application}: {title}"
                )


def score_context(context, question):
    (
        context_id,
        start_time,
        end_time,
        name,
        session_count,
        summary,
    ) = context

    text = " ".join(
        [
            str(name or ""),
            str(summary or ""),
        ]
    ).lower()

    question = question.lower()

    score = 0

    coding_questions = [
        "what was i coding",
        "what was i programming",
        "what code was i working on",
        "what was i developing",
        "what was i working on",
    ]

    research_questions = [
        "what was i researching",
        "what did i research",
        "what was i looking up",
        "what was i searching",
    ]

    recent_questions = [
        "what did i do",
        "what was i doing",
        "what happened earlier",
        "what was i working on earlier",
    ]

    coding_signals = [
        "vs code",
        "visual studio code",
        "pycharm",
        "intellij",
        "android studio",
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
        "coding",
        "code",
    ]

    research_signals = [
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

    if any(phrase in question for phrase in coding_questions):
        if any(signal in text for signal in coding_signals):
            score += 5

    if any(phrase in question for phrase in research_questions):
        if any(signal in text for signal in research_signals):
            score += 5

    if any(phrase in question for phrase in recent_questions):
        score += 2

    if "vs code" in text or "visual studio code" in text:
        score += 3

    if ".py" in text or "app.py" in text:
        score += 3

    if "coding" in text or "development" in text:
        score += 2

    try:
        start = datetime.fromisoformat(start_time)

        age_seconds = (
            datetime.now() - start
        ).total_seconds()

        if age_seconds >= 0:
            score += max(
                0,
                3 - int(age_seconds / 3600)
            )

    except (ValueError, TypeError):
        pass

    return score


def get_context_activity(context_id):
    sessions = get_context_sessions(context_id)

    activities = []

    for session in sessions:
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
                "application": application,
                "title": title,
                "start_time": start_time,
                "end_time": end_time,
            }
        )

    return activities


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

    scored_contexts = []

    for context in contexts:
        score = score_context(
            context,
            question,
        )

        if score > 0:
            scored_contexts.append(
                (
                    score,
                    context,
                )
            )

    scored_contexts.sort(
        key=lambda item: (
            item[0],
            item[1][1],
        ),
        reverse=True,
    )

    if not scored_contexts:
        print(
            "\nI couldn't find a relevant memory."
        )
        return

    top_contexts = scored_contexts[:3]

    print("\nDIGITAL MEMORY - ANSWER\n")

    first_context = top_contexts[0][1]

    activities = get_context_activity(
        first_context[0]
    )

    coding_activities = []

    for activity in activities:
        application = activity["application"]
        title = activity["title"]

        combined = (
            f"{application} {title}"
        ).lower()

        if (
            "visual studio code" in combined
            or "vs code" in combined
            or ".py" in combined
            or ".js" in combined
            or ".ts" in combined
            or ".java" in combined
            or ".cpp" in combined
            or ".c" in combined
            or ".cs" in combined
            or ".html" in combined
            or ".css" in combined
            or ".sql" in combined
        ):
            coding_activities.append(
                activity
            )

    if coding_activities:
        unique_files = []

        for activity in coding_activities:
            title = activity["title"].strip()

            if title and title not in unique_files:
                unique_files.append(title)

        print("You were working on coding/development.")

        if unique_files:
            print(
                "\nFiles/windows involved:"
            )

            for file_name in unique_files[:5]:
                print(f"  - {file_name}")

        applications = []

        for activity in coding_activities:
            app = activity["application"]

            if app and app not in applications:
                applications.append(app)

        if applications:
            print(
                "\nApplications:"
            )

            for app in applications:
                print(f"  - {app}")

    else:
        print(
            "I found these recent related contexts:"
        )

    for score, context in top_contexts:
        (
            context_id,
            start_time,
            end_time,
            name,
            session_count,
            summary,
        ) = context

        print()
        print(f"Context : {name}")
        print(f"Start   : {start_time}")
        print(f"End     : {end_time}")
        print(f"Sessions: {session_count}")

        if summary:
            print(f"Summary : {summary}")

        activities = get_context_activity(
            context_id
        )

        if activities:
            print("Activity:")

            shown = set()

            for activity in activities:
                key = (
                    activity["application"],
                    activity["title"],
                )

                if key in shown:
                    continue

                shown.add(key)

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