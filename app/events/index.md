# Events

Events record that something happened. After a successful mutation, a command builds a CloudEvent and publishes it to NATS so other systems can react.

This directory only builds outbound events. Incoming NATS messages are handled by `run_nats_worker.py` and `app/tasks/process_nats_event_task.py`.

## When to use

- A create, update, or delete should notify other systems over NATS.
- You need a stable, typed payload for a domain change (`contact.created`, `contact_list.contact_subscribed`, and so on).

## Conventions

- One file per domain at the root of this directory: `contact_events.py`, `contact_list_events.py`, `waiting_list_events.py`.
- Event types are `{entity}.{action}`: `contact.created`, `contact.updated`, `waiting_list.contact_added`.
- Each file holds type constants and `build_*` helpers that return a tessera_sdk `Event`. Builders live here, not in the command that publishes.
- Commands call a builder, then `NatsEventPublisher.publish_sync`. They do not talk to NATS directly.
- Payload data is usually the API schema dumped as JSON, plus labels/tags for the affected IDs.

## What belongs here

- Constructing CloudEvents from domain models.
- Event type constants and minimal transport metadata (source, subject, labels, tags).

## What does not belong here

- Publishing — that stays in the **command**, via `NatsEventPublisher`.
- Business rules for whether the mutation is allowed — that stays in a **command**.
- Ingesting inbound NATS messages — that stays in the worker and task layer.

Commands emit events after a successful change. Builders shape the payload; `NatsEventPublisher` delivers it.
