# Tasks

Tasks are Celery jobs that run outside the request cycle. They poll external systems on a schedule, or process work that was enqueued by a worker.

## When to use

- Work that must run periodically (Celery beat), such as polling Sendly for campaign status.
- Work that should be acknowledged quickly and finished later, such as ingesting a NATS envelope (`process_nats_event_task.delay`).

Do not put request-path mutations here. Those belong in a **command**.

## Conventions

- One file per task at the root of this directory: `poll_campaign_status.py`, `poll_campaign_engagement.py`, `process_nats_event_task.py`.
- Decorate the public entry point with `@celery_app.task` and a stable `name=` under `app.tasks.*`.
- Keep the decorated function thin: open a session with `db_session()` and call a private `_` helper. Tests call that helper directly, without Celery or NATS.
- Register the module in `_import_tasks()` in `__init__.py` so the worker discovers it.
- Periodic tasks also need a `beat_schedule` entry in `app/core/celery_app.py`.

## What belongs here

- Opening a worker-owned database session and orchestrating repositories (and external clients) for background work.
- Isolating per-item failures so one bad campaign or event does not stop the rest of a batch.

## What does not belong here

- HTTP handlers or RBAC — use a **router**.
- Building outbound CloudEvents — use an **event** builder; commands publish them.
- Raw SQLAlchemy queries — use a **repository**.

The NATS worker only enqueues. Beat only schedules. Task bodies do the work.
