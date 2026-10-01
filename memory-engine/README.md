# Digital Memory

A local-first digital memory system that captures activity, organizes it into sessions and contexts, and lets you ask questions about what you were doing.

## What it does

- Captures active Windows application activity
- Stores events locally in SQLite
- Groups activity into sessions
- Builds higher-level activity contexts
- Detects activity intent such as coding and research
- Supports natural-language memory questions
- Works offline
- Keeps memory data on the local machine

## Example

You can ask:

> What was I researching?

The system searches stored activity and returns the relevant research context.

## Architecture

Windows Activity → Events → Sessions → Contexts → SQLite → Memory Queries

## Tech Stack

- Python
- SQLite
- PyGetWindow
- Git / GitHub

## Current Status

Working prototype with Windows activity capture, persistent memory, session tracking, context detection, and memory queries.

## Privacy

The system is designed around local-first storage. Activity data is stored in the project's local SQLite database and is not automatically uploaded to a cloud service.

## Future Direction

- Android activity capture
- Cross-device synchronization
- Smarter context understanding
- Better natural-language memory retrieval
- Memory graph visualization