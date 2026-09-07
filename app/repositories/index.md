# Repositories

Repositories talk to the database. They are the only layer that should run SQLAlchemy queries and persist changes (create, update, delete).

## When to use

- You need to load, save, or remove a record.
- You need a reusable query for one entity (e.g. “all files for this person”).

## Conventions

- One file per entity: `person_repository.py`, `resource_file_repository.py`, etc.
- Methods are named after what they do: `get_person`, `create_resource_file`, `delete_will`.
- For list endpoints that use **fastapi_pagination**, expose a `*_query()` method that returns a SQLAlchemy query object—not a list from `.all()`.

## What belongs here

- Filtering, sorting, and pagination at the database level.
- Mapping between ORM models and simple create/update inputs.

## What does not belong here

- Business rules (“only the account owner may delete this”).
- Calling external APIs (Vaulta, email, etc.).
- Emitting domain events.

Routers should not call repositories directly for anything beyond trivial lookups. Prefer **queries** for reads and **commands** for writes.
