# Digital Memory

A local-first digital memory engine for capturing, organizing, and searching computer activity.

## Overview

Digital Memory is a privacy-conscious prototype that turns Windows activity into structured, searchable memory.

Instead of storing activity as isolated events, the system organizes it into:

**Events → Sessions → Contexts → Summaries**

The current version focuses on reliable local data collection and organization.

## Current Features

* Windows active-window monitoring
* Automatic event recording
* SQLite-based local persistence
* Automatic session creation
* Session-to-event relationships
* Context grouping based on activity gaps
* Automatic context summaries
* Keyword-based memory search
* Timeline view
* Time-range queries
* Session inspection
* Context inspection
* Recovery of sessions left open after interruption
* Local-first operation

## Architecture

```text
Windows Active Window
        ↓
Windows Collector
        ↓
Events
        ↓
Sessions
        ↓
Context Engine
        ↓
Contexts + Summaries
        ↓
SQLite Database
        ↓
CLI Search / Timeline / Inspection
```

## Project Structure

```text
memory-engine/
│
├── app.py
├── context_engine.py
├── memory_store.py
├── windows_collector.py
├── windows_collector.backup.py
├── README.md
└── .gitignore
```

## Requirements

* Windows
* Python 3
* Git
* Python packages used by the collector

## Running the Collector

Activate the virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Start the Windows collector:

```powershell
python windows_collector.py
```

The collector monitors the active window and records changes locally.

Press:

```text
Ctrl+C
```

to stop it safely.

## Using the Memory Interface

Run:

```powershell
python app.py
```

The current interface provides:

```text
1. Timeline
2. Search
3. Time Range
4. Sessions
5. Session Details
6. Contexts
```

## Privacy

The current implementation is local-first.

Recorded activity is stored in a local SQLite database rather than automatically being uploaded to a remote service.

The database file is intentionally excluded from Git through `.gitignore`.

## Design Goals

The project is being developed around several principles:

* Local-first data ownership
* Structured memory rather than raw logs
* Reliable persistence
* Recoverability after interruption
* Explainable context grouping
* Extensible architecture
* Cross-device memory as a future direction

## Current Status

This repository contains the working Windows MVP.

The architecture is designed to be extended toward:

* Android activity collection
* Cross-device synchronization
* richer activity-intent detection
* natural-language memory queries
* stronger privacy and security controls
* a more polished user interface

## Why This Project?

Digital activity generates large amounts of information, but most systems treat that information as isolated logs.

Digital Memory explores a different approach:

**What if device activity could become structured personal context that a user could search and understand later?**

This project is an experiment toward that idea.

## License

License to be determined.
