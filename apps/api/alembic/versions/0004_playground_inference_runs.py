"""Persist playground inference history (Phase 11)."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0004_playground_inference_runs"
down_revision = "0003_runtime_build_jobs"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "playground_inference_runs",
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
        sa.Column("input_text", sa.Text(), nullable=False),
        sa.Column("request_payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("response_payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
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
        "ix_playground_inference_runs_project_id",
        "playground_inference_runs",
        ["project_id"],
        unique=False,
    )
    op.create_index(
        "ix_playground_inference_runs_created_at",
        "playground_inference_runs",
        ["created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_playground_inference_runs_created_at", table_name="playground_inference_runs")
    op.drop_index("ix_playground_inference_runs_project_id", table_name="playground_inference_runs")
    op.drop_table("playground_inference_runs")
