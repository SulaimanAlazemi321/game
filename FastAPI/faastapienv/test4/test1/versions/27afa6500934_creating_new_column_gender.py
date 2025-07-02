"""creating new column gender

Revision ID: 27afa6500934
Revises: 
Create Date: 2025-07-02 11:01:17.770368

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '27afa6500934'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("Person", sa.Column("phone_number", sa.String(), nullable = True) )


def downgrade() -> None:
    op.drop_column("Person", "phone-number")
