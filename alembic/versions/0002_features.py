"""Add features, gates, and feature_audit_logs

Revision ID: 0002_features
Revises: initialize_database
Create Date: 2026-09-07

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0002_features"
down_revision: str | None = "initialize_database"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

gate_type_enum = postgresql.ENUM("boolean", "actor", name="gate_type")


def upgrade() -> None:
    op.create_table(
        "features",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("key", sa.String, nullable=False),
        sa.Column("description", sa.String, nullable=True),
        sa.Column(
            "created_at", sa.DateTime, nullable=False, server_default=sa.text("now()")
        ),
        sa.Column(
            "updated_at", sa.DateTime, nullable=False, server_default=sa.text("now()")
        ),
    )
    op.create_index("ix_features_key", "features", ["key"], unique=True)

    op.create_table(
        "gates",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "feature_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("features.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("gate_type", gate_type_enum, nullable=False),
        sa.Column("value", sa.String, nullable=False),
        sa.Column(
            "created_at", sa.DateTime, nullable=False, server_default=sa.text("now()")
        ),
        sa.Column(
            "updated_at", sa.DateTime, nullable=False, server_default=sa.text("now()")
        ),
    )
    op.create_index("ix_gates_feature_id", "gates", ["feature_id"])
    op.create_index(
        "uq_gates_feature_boolean",
        "gates",
        ["feature_id", "gate_type"],
        unique=True,
        postgresql_where=sa.text("gate_type = 'boolean'"),
    )
    op.create_index(
        "uq_gates_feature_actor",
        "gates",
        ["feature_id", "gate_type", "value"],
        unique=True,
        postgresql_where=sa.text("gate_type = 'actor'"),
    )

    op.create_table(
        "feature_audit_logs",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("feature_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("feature_key", sa.String, nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("action", sa.String, nullable=False),
        sa.Column("snapshot", sa.JSON, nullable=True),
        sa.Column(
            "created_at", sa.DateTime, nullable=False, server_default=sa.text("now()")
        ),
    )
    op.create_index(
        "ix_feature_audit_logs_feature_id", "feature_audit_logs", ["feature_id"]
    )


def downgrade() -> None:
    op.drop_table("feature_audit_logs")
    op.drop_table("gates")
    op.drop_table("features")
    gate_type_enum.drop(op.get_bind(), checkfirst=True)
