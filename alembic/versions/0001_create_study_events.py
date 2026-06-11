"""create study_events table

Revision ID: 0001
Revises:
Create Date: 2026-06-11

"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: Sequence[str] | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.create_table(
        "study_events",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("student_id", sa.String(length=128), nullable=False),
        sa.Column("course_id", sa.String(length=128), nullable=False),
        sa.Column("question", sa.String(length=2000), nullable=False),
        sa.Column("correct", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_study_events_student_id", "study_events", ["student_id"])
    op.create_index("ix_study_events_course_id", "study_events", ["course_id"])


def downgrade() -> None:
    op.drop_index("ix_study_events_course_id", table_name="study_events")
    op.drop_index("ix_study_events_student_id", table_name="study_events")
    op.drop_table("study_events")
