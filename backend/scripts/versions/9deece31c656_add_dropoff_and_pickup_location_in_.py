"""add dropoff and pickup location in drive table

Revision ID: 9deece31c656
Revises: baa38daca8b3
Create Date: 2024-10-17 15:12:33.878671

"""

from typing import Sequence, Union

import geoalchemy2
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "9deece31c656"
down_revision: Union[str, None] = "baa38daca8b3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.add_column(
        "drives",
        sa.Column(
            "pickup_location",
            geoalchemy2.types.Geometry(
                geometry_type="POINT",
                srid=4326,
                from_text="ST_GeomFromEWKT",
                name="geometry",
            ),
            nullable=True,
        ),
    )
    op.add_column(
        "drives",
        sa.Column(
            "dropoff_location",
            geoalchemy2.types.Geometry(
                geometry_type="POINT",
                srid=4326,
                from_text="ST_GeomFromEWKT",
                name="geometry",
            ),
            nullable=True,
        ),
    )
    op.drop_index("idx_drives_location", table_name="drives", postgresql_using="gist")

    op.drop_column("drives", "location")


def downgrade() -> None:
    op.add_column(
        "drives",
        sa.Column(
            "location",
            geoalchemy2.types.Geometry(
                geometry_type="POINT",
                srid=4326,
                from_text="ST_GeomFromEWKT",
                name="geometry",
                _spatial_index_reflected=True,
            ),
            autoincrement=False,
            nullable=True,
        ),
    )
    op.drop_index(
        "idx_drives_pickup_location", table_name="drives", postgresql_using="gist"
    )
    op.drop_index(
        "idx_drives_dropoff_location", table_name="drives", postgresql_using="gist"
    )
    op.create_index(
        "idx_drives_location",
        "drives",
        ["location"],
        unique=False,
        postgresql_using="gist",
    )
    op.drop_column("drives", "dropoff_location")
    op.drop_column("drives", "pickup_location")
