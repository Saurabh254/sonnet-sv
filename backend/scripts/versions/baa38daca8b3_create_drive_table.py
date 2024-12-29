"""create drive table

Revision ID: baa38daca8b3
Revises: 137b138d2c3e
Create Date: 2024-10-15 14:31:59.008049

"""

from typing import Sequence, Union

import geoalchemy2
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "baa38daca8b3"
down_revision: Union[str, None] = "137b138d2c3e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "drives",
        sa.Column("driver_id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
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
        sa.Column(
            "status",
            sa.Enum("ACCEPTED", "REJECTED", "CANCELED", name="drivestatus"),
            nullable=False,
        ),
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_drives_created_at"), "drives", ["created_at"], unique=False
    )
    op.create_index(op.f("ix_drives_id"), "drives", ["id"], unique=False)
    op.create_index(
        op.f("ix_drives_updated_at"), "drives", ["updated_at"], unique=False
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    op.drop_index(op.f("ix_drives_updated_at"), table_name="drives")
    op.drop_index(op.f("ix_drives_id"), table_name="drives")
    op.drop_index(op.f("ix_drives_created_at"), table_name="drives")
    op.drop_table("drives")
    op.execute("DROP TYPE drivestatus;")
    # ### end Alembic commands ###