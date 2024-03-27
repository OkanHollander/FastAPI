"""Add a phone number when creating a new user

Revision ID: 376dde444d88
Revises: 5419436f1823
Create Date: 2024-03-27 19:47:02.098727

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '376dde444d88'
down_revision: Union[str, None] = '5419436f1823'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
