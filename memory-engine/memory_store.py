import sqlite3
from pathlib import Path


DATABASE_PATH = Path(__file__).parent / "memory.db"


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database():
    connection = get_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            source TEXT NOT NULL,
            event_type TEXT NOT NULL,
            details TEXT NOT NULL,
            session_id INTEGER
        )
    """)

    columns = connection.execute(
        "PRAGMA table_info(events)"
    ).fetchall()

    column_names = [column[1] for column in columns]

    if "session_id" not in column_names:
        connection.execute(
            "ALTER TABLE events ADD COLUMN session_id INTEGER"
        )

    connection.execute("""
        CREATE INDEX IF NOT EXISTS idx_events_timestamp
        ON events(timestamp)
    """)

    connection.execute("""
        CREATE INDEX IF NOT EXISTS idx_events_source
        ON events(source)
    """)

    connection.execute("""
        CREATE INDEX IF NOT EXISTS idx_events_event_type
        ON events(event_type)
    """)

    connection.execute("""
        CREATE INDEX IF NOT EXISTS idx_events_session_id
        ON events(session_id)
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            start_time TEXT NOT NULL,
            end_time TEXT,
            application TEXT NOT NULL,
            title TEXT NOT NULL,
            event_count INTEGER NOT NULL DEFAULT 0
        )
    """)

    connection.execute("""
        CREATE INDEX IF NOT EXISTS idx_sessions_start_time
        ON sessions(start_time)
    """)

    connection.execute("""
        CREATE INDEX IF NOT EXISTS idx_sessions_application
        ON sessions(application)
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS contexts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            start_time TEXT NOT NULL,
            end_time TEXT,
            name TEXT NOT NULL,
            session_count INTEGER NOT NULL DEFAULT 0,
            summary TEXT
        )
    """)

    context_columns = connection.execute(
        "PRAGMA table_info(contexts)"
    ).fetchall()

    context_column_names = [
        column[1]
        for column in context_columns
    ]

    if "summary" not in context_column_names:
        connection.execute(
            "ALTER TABLE contexts ADD COLUMN summary TEXT"
        )

    connection.execute("""
        CREATE INDEX IF NOT EXISTS idx_contexts_start_time
        ON contexts(start_time)
    """)

    connection.execute("""
        CREATE INDEX IF NOT EXISTS idx_contexts_name
        ON contexts(name)
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS context_sessions (
            context_id INTEGER NOT NULL,
            session_id INTEGER NOT NULL,
            PRIMARY KEY (context_id, session_id),
            FOREIGN KEY (context_id) REFERENCES contexts(id),
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        )
    """)

    connection.execute("""
        CREATE INDEX IF NOT EXISTS idx_context_sessions_context
        ON context_sessions(context_id)
    """)

    connection.execute("""
        CREATE INDEX IF NOT EXISTS idx_context_sessions_session
        ON context_sessions(session_id)
    """)

    connection.commit()
    connection.close()


def save_event(
    timestamp,
    source,
    event_type,
    details,
    session_id=None
):
    connection = get_connection()

    connection.execute(
        """
        INSERT INTO events (
            timestamp,
            source,
            event_type,
            details,
            session_id
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            timestamp,
            source,
            event_type,
            details,
            session_id
        ),
    )

    connection.commit()
    connection.close()


def get_events():
    connection = get_connection()

    events = connection.execute(
        """
        SELECT
            id,
            timestamp,
            source,
            event_type,
            details,
            session_id
        FROM events
        ORDER BY timestamp DESC
        """
    ).fetchall()

    connection.close()

    return events


def get_events_between(start_time, end_time):
    connection = get_connection()

    events = connection.execute(
        """
        SELECT
            id,
            timestamp,
            source,
            event_type,
            details,
            session_id
        FROM events
        WHERE timestamp >= ?
          AND timestamp <= ?
        ORDER BY timestamp DESC
        """,
        (
            start_time,
            end_time
        ),
    ).fetchall()

    connection.close()

    return events


def create_session(start_time, application, title):
    connection = get_connection()

    cursor = connection.execute(
        """
        INSERT INTO sessions (
            start_time,
            application,
            title,
            event_count
        )
        VALUES (?, ?, ?, 0)
        """,
        (
            start_time,
            application,
            title
        ),
    )

    session_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return session_id


def close_session(session_id, end_time):
    connection = get_connection()

    connection.execute(
        """
        UPDATE sessions
        SET end_time = ?
        WHERE id = ?
          AND end_time IS NULL
        """,
        (
            end_time,
            session_id
        ),
    )

    connection.commit()
    connection.close()


def close_open_sessions(end_time):
    connection = get_connection()

    connection.execute(
        """
        UPDATE sessions
        SET end_time = ?
        WHERE end_time IS NULL
        """,
        (end_time,),
    )

    connection.commit()
    connection.close()


def increment_session_event_count(session_id):
    connection = get_connection()

    connection.execute(
        """
        UPDATE sessions
        SET event_count = event_count + 1
        WHERE id = ?
        """,
        (session_id,),
    )

    connection.commit()
    connection.close()


def get_sessions():
    connection = get_connection()

    sessions = connection.execute(
        """
        SELECT
            id,
            start_time,
            end_time,
            application,
            title,
            event_count
        FROM sessions
        ORDER BY start_time DESC
        """
    ).fetchall()

    connection.close()

    return sessions


def get_sessions_between(start_time, end_time):
    connection = get_connection()

    sessions = connection.execute(
        """
        SELECT
            id,
            start_time,
            end_time,
            application,
            title,
            event_count
        FROM sessions
        WHERE start_time <= ?
          AND (
              end_time IS NULL
              OR end_time >= ?
          )
        ORDER BY start_time DESC
        """,
        (
            end_time,
            start_time
        ),
    ).fetchall()

    connection.close()

    return sessions


def get_session_events(session_id):
    connection = get_connection()

    events = connection.execute(
        """
        SELECT
            id,
            timestamp,
            source,
            event_type,
            details,
            session_id
        FROM events
        WHERE session_id = ?
        ORDER BY timestamp ASC
        """,
        (session_id,),
    ).fetchall()

    connection.close()

    return events


def create_context(start_time, name):
    connection = get_connection()

    cursor = connection.execute(
        """
        INSERT INTO contexts (
            start_time,
            name,
            session_count,
            summary
        )
        VALUES (?, ?, 0, NULL)
        """,
        (
            start_time,
            name
        ),
    )

    context_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return context_id


def close_context(context_id, end_time):
    connection = get_connection()

    connection.execute(
        """
        UPDATE contexts
        SET end_time = ?
        WHERE id = ?
        """,
        (
            end_time,
            context_id
        ),
    )

    connection.commit()
    connection.close()


def add_session_to_context(context_id, session_id):
    connection = get_connection()

    connection.execute(
        """
        INSERT OR IGNORE INTO context_sessions (
            context_id,
            session_id
        )
        VALUES (?, ?)
        """,
        (
            context_id,
            session_id
        ),
    )

    connection.execute(
        """
        UPDATE contexts
        SET session_count = (
            SELECT COUNT(*)
            FROM context_sessions
            WHERE context_id = ?
        )
        WHERE id = ?
        """,
        (
            context_id,
            context_id
        ),
    )

    connection.commit()
    connection.close()


def clear_contexts():
    connection = get_connection()

    connection.execute(
        "DELETE FROM context_sessions"
    )

    connection.execute(
        "DELETE FROM contexts"
    )

    connection.commit()
    connection.close()


def get_contexts():
    connection = get_connection()

    contexts = connection.execute(
        """
        SELECT
            id,
            start_time,
            end_time,
            name,
            session_count,
            summary
        FROM contexts
        ORDER BY start_time DESC
        """
    ).fetchall()

    connection.close()

    return contexts


def get_context_sessions(context_id):
    connection = get_connection()

    sessions = connection.execute(
        """
        SELECT
            sessions.id,
            sessions.start_time,
            sessions.end_time,
            sessions.application,
            sessions.title,
            sessions.event_count
        FROM sessions
        INNER JOIN context_sessions
            ON sessions.id = context_sessions.session_id
        WHERE context_sessions.context_id = ?
        ORDER BY sessions.start_time ASC
        """,
        (context_id,),
    ).fetchall()

    connection.close()

    return sessions