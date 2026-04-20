from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "20260417_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")
    op.create_table(
        "registros_rojos",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("sorteo_id", postgresql.UUID(as_uuid=True), nullable=False, unique=True),
        sa.Column("legajo", sa.String(length=50), nullable=False),
        sa.Column("nombre", sa.String(length=100), nullable=False),
        sa.Column("apellido", sa.String(length=100), nullable=False),
        sa.Column("foto_path", sa.String(length=300), nullable=True),
        sa.Column("fecha_hora", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("email_enviado", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("email_intentos", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("email_error", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("registros_rojos")
