# Commands

Commands change state. They perform actions: create, update, delete, import, send an invitation, compute and store a score.

## When to use

- A router handles POST, PUT, PATCH, or DELETE (or any endpoint that mutates data).
- Several steps must run together (validate → save → emit event).

## Conventions

- One subdirectory per domain: `wills/`, `resource_files/`, etc.
- One class per operation: `CreateResourceFileCommand`, `DeleteWillCommand`.
- Each class exposes a single public `execute()` method.
- If you need another operation, add another command class.

## What belongs here

- Business rules and validation before persisting.
- Orchestrating repositories (and sometimes queries) to complete a use case.
- Dispatching domain events after a successful change.

## What does not belong here

- Simple read-only endpoints—use a **query** instead.
- Raw SQLAlchemy queries—use a **repository**.

Routers call commands for writes. Commands call repositories (and occasionally queries or external services). They do not replace repositories for basic data access.
