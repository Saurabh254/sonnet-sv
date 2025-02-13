"""create vehicle table

Revision ID: 137b138d2c3e
Revises: 5fdb54d8f27a
Create Date: 2024-10-13 23:28:53.399300

"""

from typing import Sequence, Union

import geoalchemy2
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "137b138d2c3e"
down_revision: Union[str, None] = "5fdb54d8f27a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "drivers",
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("phone", sa.String(), nullable=False),
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_drivers_created_at"), "drivers", ["created_at"], unique=False
    )
    op.create_index(op.f("ix_drivers_id"), "drivers", ["id"], unique=False)
    op.create_index(
        op.f("ix_drivers_updated_at"), "drivers", ["updated_at"], unique=False
    )
    op.create_table(
        "vehicle",
        sa.Column("license_number", sa.String(length=50), nullable=False),
        sa.Column("registration_number", sa.String(length=100), nullable=False),
        sa.Column("capacity", sa.Integer(), nullable=False),
        sa.Column("driver_id", sa.String(), nullable=False),
        sa.Column(
            "location",
            geoalchemy2.types.Geometry(
                geometry_type="POINT",
                srid=4326,
                from_text="ST_GeomFromEWKT",
                name="geometry",
            ),
            nullable=True,
        ),
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["driver_id"],
            ["drivers.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("license_number"),
        sa.UniqueConstraint("registration_number"),
    )

    op.create_index(
        op.f("ix_vehicle_created_at"), "vehicle", ["created_at"], unique=False
    )
    op.create_index(op.f("ix_vehicle_id"), "vehicle", ["id"], unique=True)
    op.create_index(
        op.f("ix_vehicle_updated_at"), "vehicle", ["updated_at"], unique=False
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###

    op.drop_index(op.f("ix_vehicle_updated_at"), table_name="vehicle")
    op.drop_index(op.f("ix_vehicle_id"), table_name="vehicle")
    op.drop_index(op.f("ix_vehicle_created_at"), table_name="vehicle")
    op.drop_index("idx_vehicle_location", table_name="vehicle", postgresql_using="gist")
    op.drop_table("vehicle")
    op.drop_index(op.f("ix_drivers_updated_at"), table_name="drivers")
    op.drop_index(op.f("ix_drivers_id"), table_name="drivers")
    op.drop_index(op.f("ix_drivers_created_at"), table_name="drivers")
    op.drop_table("drivers")
    # ### end Alembic commands ###
