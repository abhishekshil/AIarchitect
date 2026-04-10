"""Per-node onboarding state for guided task completion (Phase 9)."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0002_onboarding_task_progress"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "onboarding_task_progress",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("requirement_profile_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("task_graph_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("node_id", sa.String(length=256), nullable=False),
        sa.Column("state", sa.String(length=32), nullable=False),
        sa.Column("response", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("validation_feedback", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["requirement_profile_id"], ["requirement_profiles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["task_graph_id"], ["task_graphs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("task_graph_id", "node_id", name="uq_onboarding_progress_graph_node"),
    )
    op.create_index(
        "ix_onboarding_task_progress_project_id",
        "onboarding_task_progress",
        ["project_id"],
        unique=False,
    )
    op.create_index(
        "ix_onboarding_task_progress_requirement_profile_id",
        "onboarding_task_progress",
        ["requirement_profile_id"],
        unique=False,
    )
    op.create_index(
        "ix_onboarding_task_progress_task_graph_id",
        "onboarding_task_progress",
        ["task_graph_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_onboarding_task_progress_task_graph_id", table_name="onboarding_task_progress")
    op.drop_index(
        "ix_onboarding_task_progress_requirement_profile_id",
        table_name="onboarding_task_progress",
    )
    op.drop_index("ix_onboarding_task_progress_project_id", table_name="onboarding_task_progress")
    op.drop_table("onboarding_task_progress")
