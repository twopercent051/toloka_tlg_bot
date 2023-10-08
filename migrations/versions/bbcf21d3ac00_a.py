"""a

Revision ID: bbcf21d3ac00
Revises: f37b8be3a3d3
Create Date: 2023-08-31 13:16:59.742115

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bbcf21d3ac00'
down_revision: Union[str, None] = 'f37b8be3a3d3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('followings', sa.Column('create_dtime', sa.DateTime(), server_default=sa.text("TIMEZONE('utc', CURRENT_TIMESTAMP)"), nullable=False))
    op.add_column('reposts', sa.Column('create_dtime', sa.DateTime(), server_default=sa.text("TIMEZONE('utc', CURRENT_TIMESTAMP)"), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('reposts', 'create_dtime')
    op.drop_column('followings', 'create_dtime')
    # ### end Alembic commands ###