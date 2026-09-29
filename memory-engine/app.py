from datetime import datetime
import json

from memory_store import (
    initialize_database,
    get_events,
    get_events_between,
    get_sessions,
    get_session_events,
    get_contexts,
    get_context_sessions,
)


def display_timeline():
    events = get_events()

    print("\n" + "=" * 60)
    print("DIGITAL MEMORY - TIMELINE")
    print("=" * 60)

    if not events:
        print("No memories recorded yet.")
        return

    for (
        event_id,
        timestamp,
        source,
        event_type,
        details,
        session_id
    ) in events:

        print(f"\nID        : {event_id}")
        print(f"Time      : {timestamp}")
        print(f"Source    : {source}")
        print(f"Event     : {event_type}")
        print(f"Session   : {session_id}")
        print(f"Details   : {details}")

    print("\n" + "=" * 60)
    print(f"Total memories: {len(events)}")
    print("=" * 60)


def search_memories(keyword):
    events = get_events()
    sessions = get_sessions()

    keyword = keyword.lower().strip()

    matches = []

    for event in events:
        (
            event_id,
            timestamp,
            source,
            event_type,
            details,
            session_id
        ) = event

        searchable_text = (
            f"{timestamp} "
            f"{source} "
            f"{event_type} "
            f"{details}"
        ).lower()

        if keyword in searchable_text:
            matches.append(event)

    print("\n" + "=" * 60)
    print(f"DIGITAL MEMORY - SEARCH: {keyword}")
    print("=" * 60)

    if not matches:
        print("No matching memories found.")
        return

    for (
        event_id,
        timestamp,
        source,
        event_type,
        details,
        session_id
    ) in matches:

        print("\n" + "-" * 60)

        print(f"Event ID : {event_id}")
        print(f"Time     : {timestamp}")
        print(f"Source   : {source}")
        print(f"Type     : {event_type}")
        print(f"Session  : {session_id}")

        try:
            parsed_details = json.loads(details)

            print(
                f"Window   : "
                f"{parsed_details.get('window_title', details)}"
            )

        except (json.JSONDecodeError, TypeError):
            print(f"Details  : {details}")

        if session_id is not None:
            matching_session = None

            for session in sessions:
                if session[0] == session_id:
                    matching_session = session
                    break

            if matching_session is not None:
                (
                    sid,
                    start_time,
                    end_time,
                    application,
                    title,
                    event_count
                ) = matching_session

                print("\nSession context:")
                print(f"  Application : {application}")
                print(f"  Title       : {title}")
                print(f"  Start       : {start_time}")
                print(f"  End         : {end_time}")
                print(f"  Event count : {event_count}")

                session_events = get_session_events(sid)

                if len(session_events) > 1:
                    print("\n  Other events in this session:")

                    for session_event in session_events:
                        (
                            other_event_id,
                            other_timestamp,
                            other_source,
                            other_event_type,
                            other_details,
                            other_session_id
                        ) = session_event

                        if other_event_id == event_id:
                            continue

                        try:
                            other_details_json = json.loads(
                                other_details
                            )

                            other_window = other_details_json.get(
                                "window_title",
                                other_details
                            )

                        except (
                            json.JSONDecodeError,
                            TypeError
                        ):
                            other_window = other_details

                        print(
                            f"  - Event {other_event_id}: "
                            f"{other_timestamp} | "
                            f"{other_window}"
                        )

        else:
            print("\nSession context:")
            print("  This event was recorded before session linking.")

    print("\n" + "=" * 60)
    print(f"Matches: {len(matches)}")
    print("=" * 60)


def display_time_range():
    print("\n" + "=" * 60)
    print("DIGITAL MEMORY - TIME RANGE")
    print("=" * 60)

    start_time = input(
        "Start time (YYYY-MM-DD HH:MM): "
    ).strip()

    end_time = input(
        "End time (YYYY-MM-DD HH:MM): "
    ).strip()

    try:
        start = datetime.strptime(
            start_time,
            "%Y-%m-%d %H:%M"
        )

        end = datetime.strptime(
            end_time,
            "%Y-%m-%d %H:%M"
        )

    except ValueError:
        print(
            "\nInvalid time format."
            "\nUse: YYYY-MM-DD HH:MM"
        )
        return

    if start > end:
        print("\nStart time cannot be after end time.")
        return

    events = get_events_between(
        start.isoformat(),
        end.isoformat()
    )

    print("\n" + "=" * 60)
    print(
        f"MEMORIES FROM {start_time} "
        f"TO {end_time}"
    )
    print("=" * 60)

    if not events:
        print("No memories found in this time range.")
        return

    for (
        event_id,
        timestamp,
        source,
        event_type,
        details,
        session_id
    ) in events:

        print(f"\nID        : {event_id}")
        print(f"Time      : {timestamp}")
        print(f"Source    : {source}")
        print(f"Event     : {event_type}")
        print(f"Session   : {session_id}")
        print(f"Details   : {details}")

    print("\n" + "=" * 60)
    print(f"Memories found: {len(events)}")
    print("=" * 60)


def display_sessions():
    sessions = get_sessions()

    print("\n" + "=" * 60)
    print("DIGITAL MEMORY - SESSIONS")
    print("=" * 60)

    if not sessions:
        print("No sessions recorded yet.")
        return

    for (
        session_id,
        start_time,
        end_time,
        application,
        title,
        event_count
    ) in sessions:

        print(f"\nSession ID : {session_id}")
        print(f"Application: {application}")
        print(f"Title      : {title}")
        print(f"Start      : {start_time}")
        print(f"End        : {end_time}")
        print(f"Events     : {event_count}")

    print("\n" + "=" * 60)
    print(f"Total sessions: {len(sessions)}")
    print("=" * 60)


def display_session_details():
    sessions = get_sessions()

    print("\n" + "=" * 60)
    print("DIGITAL MEMORY - SESSION DETAILS")
    print("=" * 60)

    if not sessions:
        print("No sessions recorded yet.")
        return

    for (
        session_id,
        start_time,
        end_time,
        application,
        title,
        event_count
    ) in sessions:

        print(
            f"\n{session_id}. "
            f"{application} | {title}"
        )

    print("\n" + "-" * 60)

    choice = input("Enter session ID: ").strip()

    try:
        session_id = int(choice)
    except ValueError:
        print("\nInvalid session ID.")
        return

    selected_session = None

    for session in sessions:
        if session[0] == session_id:
            selected_session = session
            break

    if selected_session is None:
        print("\nSession not found.")
        return

    (
        session_id,
        start_time,
        end_time,
        application,
        title,
        event_count
    ) = selected_session

    events = get_session_events(session_id)

    print("\n" + "=" * 60)
    print(f"SESSION {session_id}")
    print("=" * 60)

    print(f"\nApplication : {application}")
    print(f"Title       : {title}")
    print(f"Start       : {start_time}")
    print(f"End         : {end_time}")
    print(f"Event count : {event_count}")

    print("\nEvents:")

    if not events:
        print("  No events linked to this session.")
    else:
        for (
            event_id,
            timestamp,
            source,
            event_type,
            details,
            linked_session_id
        ) in events:

            print(f"\n  Event ID : {event_id}")
            print(f"  Time     : {timestamp}")
            print(f"  Source   : {source}")
            print(f"  Type     : {event_type}")

            try:
                parsed_details = json.loads(details)

                print(
                    f"  Window   : "
                    f"{parsed_details.get('window_title', details)}"
                )

            except (json.JSONDecodeError, TypeError):
                print(f"  Details  : {details}")

            print(
                f"  Session  : {linked_session_id}"
            )

    print("\n" + "=" * 60)


def display_contexts():
    contexts = get_contexts()

    print("\n" + "=" * 60)
    print("DIGITAL MEMORY - CONTEXTS")
    print("=" * 60)

    if not contexts:
        print("No contexts recorded yet.")
        return

    for context in contexts:
        (
            context_id,
            start_time,
            end_time,
            name,
            session_count
        ) = context[:5]

        summary = None

        if len(context) > 5:
            summary = context[5]

        print(f"\nContext ID : {context_id}")
        print(f"Name       : {name}")
        print(f"Start      : {start_time}")
        print(f"End        : {end_time}")
        print(f"Sessions   : {session_count}")

        print("\nSummary:")
        if summary:
            print(f"  {summary}")
        else:
            print("  No summary available.")

        sessions = get_context_sessions(context_id)

        if sessions:
            print("\n  Sessions:")

            for (
                session_id,
                session_start,
                session_end,
                application,
                title,
                event_count
            ) in sessions:

                print(
                    f"  - Session {session_id}: "
                    f"{application} | {title}"
                )

    print("\n" + "=" * 60)
    print(f"Total contexts: {len(contexts)}")
    print("=" * 60)


def main():
    initialize_database()

    print("\nDigital Memory")
    print("1. Timeline")
    print("2. Search")
    print("3. Time Range")
    print("4. Sessions")
    print("5. Session Details")
    print("6. Contexts")

    choice = input("\nChoose an option: ").strip()

    if choice == "1":
        display_timeline()

    elif choice == "2":
        keyword = input("Search memories: ").strip()

        if keyword:
            search_memories(keyword)
        else:
            print("Search keyword cannot be empty.")

    elif choice == "3":
        display_time_range()

    elif choice == "4":
        display_sessions()

    elif choice == "5":
        display_session_details()

    elif choice == "6":
        display_contexts()

    else:
        print("Invalid option.")


if __name__ == "__main__":
    main()