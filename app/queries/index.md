# Queries

Queries read data. They answer questions like “what files does this person have?” or “what is on this page?” without changing anything in the database.

## When to use

- A router needs to return data (GET / list endpoints).
- You need to combine repository results with other read-only sources (e.g. enriching records with metadata from Vaulta).

## Conventions

- One subdirectory per domain: `resource_files/`, `persons/`, etc.
- One class per operation: `GetResourceFilesQuery`.
- Each class exposes a single public `execute()` method.
- If you need more than one read operation, add another query class—do not grow one class with many methods.

## What belongs here

- Calling repositories to load data.
- Read-only calls to external services.
- Shaping results into Pydantic schemas for the API.

## What does not belong here

- Creates, updates, or deletes.
- Dispatching events.
- Authorization decisions that gate a mutation (those live in commands or policies).

Routers call queries for reads. Commands may call queries when a write needs existing state first, but queries should not call commands.
