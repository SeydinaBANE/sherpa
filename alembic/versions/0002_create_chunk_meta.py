"""create chunk_meta table

Revision ID: 0002
Revises: 0001
Create Date: 2026-06-11

"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: Sequence[str] | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.create_table(
        "chunk_meta",
        sa.Column("chunk_id", sa.String(length=64), primary_key=True),
        sa.Column("course_id", sa.String(length=128), nullable=False),
        sa.Column("source", sa.String(length=256), nullable=False),
        sa.Column("ordinal", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_chunk_meta_course_id", "chunk_meta", ["course_id"])


def downgrade() -> None:
    op.drop_index("ix_chunk_meta_course_id", table_name="chunk_meta")
    op.drop_table("chunk_meta")
