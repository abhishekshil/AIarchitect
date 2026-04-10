"""Persist generated integration code snippet bundles (Phase 12)."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0005_code_snippet_bundles"
down_revision = "0004_playground_inference_runs"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "code_snippet_bundles",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("runtime_graph_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("runtime_graph_version", sa.Integer(), nullable=False),
        sa.Column("architecture_pattern", sa.String(length=64), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["runtime_graph_id"], ["runtime_graphs.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_code_snippet_bundles_project_created",
        "code_snippet_bundles",
        ["project_id", "created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_code_snippet_bundles_project_created", table_name="code_snippet_bundles")
    op.drop_table("code_snippet_bundles")
