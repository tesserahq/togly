# Models

Models are SQLAlchemy ORM entities. They define tables, columns, and relationships. They are persistence shapes, not API contracts.

## When to use

- Adding a new table or column.
- Declaring a relationship between entities.

Do not put request/response shapes here — those belong in **schemas**. Do not put SQL or business rules here — those belong in a **repository** or **command**.

## Conventions

- One file per entity at the root of this directory: `contact.py`, `campaign.py`, `segment.py`.
- Inherit `Base` from `app.db`. Use UUID primary keys (`default=uuid.uuid4`).
- Add `TimestampMixin` on nearly every table. Add `SoftDeleteMixin` on first-class entities (`Contact`, `Campaign`, `Tag`, …). Soft-deleted rows are hidden automatically by `app.db._add_soft_delete_criteria`.
- Current-state assignment rows skip `SoftDeleteMixin` (`ContactTag`, `CampaignTag`, `ContactCustomFieldValue`). Removing an assignment is a hard delete, distinct from soft-deleting the parent.
- Uniqueness among active rows is usually a partial index in the migration, not a column-level constraint, so a soft-deleted name or `event_type` can be reused.
- Export new models from `__init__.py`. Workers import `app.models` so relationships resolve before any query runs.
- Schema changes go through Alembic. Do not create or alter tables from the model class.

## What belongs here

- Columns, foreign keys, table constraints, and ORM relationships.
- Small derived properties that read already-loaded state (`Contact.full_name`, `Campaign.tags`).

## What does not belong here

- HTTP or Pydantic request/response models — use a **schema**.
- Queries, filters, and persistence — use a **repository**.
- Validation of whether a mutation is allowed — use a **command**.

Repositories load and save models. Schemas serialize them. Commands decide when they change.
