from datetime import datetime

from memory_store import (
    create_context,
    close_context,
    add_session_to_context,
    clear_contexts,
    get_sessions,
)


CONTEXT_GAP_MINUTES = 5


def parse_time(timestamp):
    return datetime.fromisoformat(timestamp)


def should_continue_context(previous_session, current_session):
    previous_end = previous_session[2]
    current_start = current_session[1]

    if previous_end is None:
        return True

    previous_end_time = parse_time(previous_end)
    current_start_time = parse_time(current_start)

    gap = current_start_time - previous_end_time

    return gap.total_seconds() <= CONTEXT_GAP_MINUTES * 60


def clean_application_name(application):
    application = application.strip()

    if application.lower() in {
        "visual studio code",
        "code",
    }:
        return "VS Code"

    if application.lower() == "google chrome":
        return "Chrome"

    return application


def generate_context_name(sessions):
    applications = []

    for session in sessions:
        application = clean_application_name(
            session[3]
        )

        if application and application not in applications:
            applications.append(application)

    if not applications:
        return "General Activity"

    if len(applications) == 1:
        return applications[0]

    if len(applications) == 2:
        return f"{applications[0]} + {applications[1]}"

    return " + ".join(applications[:3]) + " + More"


def detect_activity_intent(sessions):
    applications = []
    titles = []

    for session in sessions:
        application = clean_application_name(
            session[3]
        ).lower()

        title = session[4].strip().lower()

        if application:
            applications.append(application)

        if title:
            titles.append(title)

    application_text = " ".join(applications)
    title_text = " ".join(titles)

    coding_signals = [
        "vs code",
        "visual studio",
        "pycharm",
        "intellij",
        "android studio",
        "terminal",
        "powershell",
        "command prompt",
        "cmd",
    ]

    coding_file_signals = [
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

    research_signals = [
        "chrome",
        "edge",
        "firefox",
        "google",
        "search",
        "stackoverflow",
        "github",
        "documentation",
        "docs",
        "wikipedia",
    ]

    writing_signals = [
        "word",
        "notepad",
        "google docs",
        "microsoft word",
    ]

    communication_signals = [
        "teams",
        "slack",
        "discord",
        "whatsapp",
        "telegram",
        "outlook",
        "gmail",
    ]

    coding_detected = (
        any(
            signal in application_text
            for signal in coding_signals
        )
        or any(
            signal in title_text
            for signal in coding_file_signals
        )
    )

    research_detected = any(
        signal in application_text
        or signal in title_text
        for signal in research_signals
    )

    writing_detected = any(
        signal in application_text
        or signal in title_text
        for signal in writing_signals
    )

    communication_detected = any(
        signal in application_text
        or signal in title_text
        for signal in communication_signals
    )

    if coding_detected and research_detected:
        return "Coding + Research"

    if coding_detected:
        return "Coding"

    if research_detected:
        return "Research"

    if writing_detected:
        return "Writing"

    if communication_detected:
        return "Communication"

    return "General Activity"


def generate_context_summary(sessions):
    applications = []
    titles = []

    for session in sessions:
        application = clean_application_name(
            session[3]
        )

        title = session[4].strip()

        if application and application not in applications:
            applications.append(application)

        if title and title not in titles:
            titles.append(title)

    if not applications:
        return "Intent: General Activity."

    intent = detect_activity_intent(sessions)

    application_text = ", ".join(applications)

    summary = (
        f"Intent: {intent}. "
        f"Activity involved {application_text}."
    )

    if titles:
        important_titles = titles[:3]

        title_text = ", ".join(
            important_titles
        )

        summary += (
            f" Related windows included "
            f"{title_text}."
        )

    return summary


def save_context_metadata(context_id, name, summary):
    import sqlite3

    from memory_store import DATABASE_PATH

    connection = sqlite3.connect(DATABASE_PATH)

    columns = connection.execute(
        "PRAGMA table_info(contexts)"
    ).fetchall()

    column_names = [
        column[1]
        for column in columns
    ]

    if "summary" not in column_names:
        connection.execute(
            """
            ALTER TABLE contexts
            ADD COLUMN summary TEXT
            """
        )

    connection.execute(
        """
        UPDATE contexts
        SET name = ?,
            summary = ?
        WHERE id = ?
        """,
        (
            name,
            summary,
            context_id,
        ),
    )

    connection.commit()
    connection.close()


def build_contexts():
    sessions = get_sessions()

    if not sessions:
        print("No sessions available.")
        return []

    clear_contexts()

    sessions = sorted(
        sessions,
        key=lambda session: session[1],
    )

    contexts = []

    current_sessions = []
    current_context_id = None
    previous_session = None

    for session in sessions:

        if current_context_id is None:
            current_context_id = create_context(
                start_time=session[1],
                name="Temporary Context",
            )

            current_sessions = [session]

            add_session_to_context(
                context_id=current_context_id,
                session_id=session[0],
            )

        elif should_continue_context(
            previous_session,
            session,
        ):
            current_sessions.append(session)

            add_session_to_context(
                context_id=current_context_id,
                session_id=session[0],
            )

        else:
            context_name = generate_context_name(
                current_sessions
            )

            context_summary = generate_context_summary(
                current_sessions
            )

            close_context(
                context_id=current_context_id,
                end_time=previous_session[2],
            )

            save_context_metadata(
                context_id=current_context_id,
                name=context_name,
                summary=context_summary,
            )

            contexts.append(
                {
                    "id": current_context_id,
                    "name": context_name,
                    "summary": context_summary,
                }
            )

            current_context_id = create_context(
                start_time=session[1],
                name="Temporary Context",
            )

            current_sessions = [session]

            add_session_to_context(
                context_id=current_context_id,
                session_id=session[0],
            )

        previous_session = session

    if current_context_id is not None:
        context_name = generate_context_name(
            current_sessions
        )

        context_summary = generate_context_summary(
            current_sessions
        )

        last_end = current_sessions[-1][2]

        if last_end is not None:
            close_context(
                context_id=current_context_id,
                end_time=last_end,
            )

        save_context_metadata(
            context_id=current_context_id,
            name=context_name,
            summary=context_summary,
        )

        contexts.append(
            {
                "id": current_context_id,
                "name": context_name,
                "summary": context_summary,
            }
        )

    return contexts


if __name__ == "__main__":
    build_contexts()
    print("Context building completed.")