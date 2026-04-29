from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "20260429_01"
down_revision = "20260417_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    rol_usuario = postgresql.ENUM("admin", "rrhh", name="rol_usuario", create_type=False)
    tipo_auth_token = postgresql.ENUM("set_password", "reset_password", name="tipo_auth_token", create_type=False)
    postgresql.ENUM("admin", "rrhh", name="rol_usuario").create(op.get_bind(), checkfirst=True)
    postgresql.ENUM("set_password", "reset_password", name="tipo_auth_token").create(op.get_bind(), checkfirst=True)

    op.add_column(
        "registros_rojos",
        sa.Column("estado_control", sa.String(length=20), nullable=False, server_default=sa.text("'pendiente'")),
    )
    op.add_column("registros_rojos", sa.Column("fecha_control", sa.DateTime(timezone=True), nullable=True))
    op.add_column("registros_rojos", sa.Column("observacion_control", sa.Text(), nullable=True))

    op.create_table(
        "usuarios_dashboard",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("nombre", sa.String(length=100), nullable=False),
        sa.Column("apellido", sa.String(length=100), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False, unique=True),
        sa.Column("rol", rol_usuario, nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("activo", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("ultimo_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_table(
        "auth_tokens",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("usuarios_dashboard.id", ondelete="CASCADE"), nullable=False),
        sa.Column("token_hash", sa.String(length=255), nullable=False, unique=True),
        sa.Column("tipo", tipo_auth_token, nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )


def downgrade() -> None:
    op.drop_table("auth_tokens")
    op.drop_table("usuarios_dashboard")
    op.drop_column("registros_rojos", "observacion_control")
    op.drop_column("registros_rojos", "fecha_control")
    op.drop_column("registros_rojos", "estado_control")
    tipo_auth_token = sa.Enum("set_password", "reset_password", name="tipo_auth_token")
    rol_usuario = sa.Enum("admin", "rrhh", name="rol_usuario")
    tipo_auth_token.drop(op.get_bind(), checkfirst=True)
    rol_usuario.drop(op.get_bind(), checkfirst=True)
