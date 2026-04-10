"""Runtime graph build job queue + status (Phase 10 skeleton)."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0003_runtime_build_jobs"
down_revision = "0002_onboarding_task_progress"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "runtime_build_jobs",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("requirement_profile_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("solution_candidate_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("stage", sa.String(length=128), nullable=False, server_default="queued"),
        sa.Column("error_detail", sa.Text(), nullable=True),
        sa.Column("runtime_graph_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("runtime_graph_version", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["requirement_profile_id"],
            ["requirement_profiles.id"],
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["solution_candidate_id"],
            ["solution_candidates.id"],
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(["runtime_graph_id"], ["runtime_graphs.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_runtime_build_jobs_project_id",
        "runtime_build_jobs",
        ["project_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_runtime_build_jobs_project_id", table_name="runtime_build_jobs")
    op.drop_table("runtime_build_jobs")
