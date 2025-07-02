"""creating new column gender

Revision ID: c8f773ab5490
Revises: 27afa6500934
Create Date: 2025-07-02 11:14:14.847172

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c8f773ab5490'
down_revision: Union[str, Sequence[str], None] = '27afa6500934'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
