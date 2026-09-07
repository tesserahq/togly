"""Initialize the database

Revision ID: initialize_database
Revises:
Create Date: 2024-03-21

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "initialize_database"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


FTS_EXPR = " || ".join(
    [
        "setweight(to_tsvector('simple_unaccent', coalesce(first_name,'')), 'A')",
        "setweight(to_tsvector('simple_unaccent', coalesce(middle_name,'')), 'B')",
        "setweight(to_tsvector('simple_unaccent', coalesce(last_name,'')), 'A')",
        "setweight(to_tsvector('simple_unaccent', coalesce(company,'')), 'A')",
        "setweight(to_tsvector('simple_unaccent', coalesce(job,'')), 'B')",
        "setweight(to_tsvector('simple_unaccent', coalesce(email,'')), 'B')",
        "setweight(to_tsvector('simple_unaccent', coalesce(phone,'')), 'C')",
        "setweight(to_tsvector('simple_unaccent', coalesce(notes,'')), 'C')",
        "setweight(to_tsvector('simple_unaccent', coalesce(address_line_1,'')), 'D')",
        "setweight(to_tsvector('simple_unaccent', coalesce(address_line_2,'')), 'D')",
        "setweight(to_tsvector('simple_unaccent', coalesce(city,'')), 'D')",
        "setweight(to_tsvector('simple_unaccent', coalesce(state,'')), 'D')",
        "setweight(to_tsvector('simple_unaccent', coalesce(zip_code,'')), 'D')",
        "setweight(to_tsvector('simple_unaccent', coalesce(country,'')), 'D')",
    ]
)


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("email", sa.String, unique=True, nullable=True),
        sa.Column("external_id", sa.String, nullable=True),
        sa.Column(
            "attributes",
            postgresql.JSONB,
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "created_at", sa.DateTime, nullable=False, server_default=sa.text("now()")
        ),
        sa.Column(
            "updated_at", sa.DateTime, nullable=False, server_default=sa.text("now()")
        ),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
    )

    # Add a partial unique index for external_id
    op.create_index(
        "uq_users_external_id",
        "users",
        ["external_id"],
        unique=True,
        postgresql_where=sa.text("external_id IS NOT NULL"),
    )


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table("users")
