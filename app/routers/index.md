# Routers

Routers are FastAPI route handlers. They accept HTTP requests, authorize them, and delegate work to commands (writes) or queries (reads).

This service exposes a single API. Do not split endpoints by audience (customer vs staff) or access scope.

## When to use

- Exposing a new HTTP endpoint.
- Adding a nested resource under an existing parent path (e.g. interactions under a contact).

## Conventions

- One file per domain at the root of this directory: `contact.py`, `campaign.py`, `segment.py`.
- One `APIRouter` per module, with a path prefix and tags. If a resource is nested under a parent, add a second `nested_router` in the same file (see `contact_interaction.py`, `custom_field.py`).
- Register each router in `app/main.py` with `app.include_router`.
- Authorize with `build_rbac_dependencies(resource=...)` and `Depends(rbac["create"|"read"|"update"|"delete"])`.
- Resolve path entities via `utils/dependencies.py` (`get_contact_by_id`, `get_campaign_by_id`, …).
- Keep handlers thin. Writes go to a command; reads go to a query (or a repository `*_query()` for paginated lists).
- For listing endpoints, use `fastapi_pagination` unless there is a strict reason not to.

## What belongs here

- HTTP mapping: status codes, request/response schemas, pagination.
- Auth and RBAC dependencies.
- Translating command/query failures into HTTP errors.

## What does not belong here

- Business rules and multi-step writes — use a **command**.
- Combining read sources or shaping read models — use a **query**.
- SQLAlchemy queries — use a **repository**.

## Adding a new router module

1. Create `app/routers/{domain}.py` with an `APIRouter` (and `nested_router` if needed).
2. Include it in `app/main.py` with `app.include_router`.
3. Export it from `__init__.py` if other modules import the package.
4. Reuse shared dependencies from `utils/dependencies.py` where possible.
