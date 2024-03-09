"""empty message

Revision ID: 49fb10d64fa8
Revises: ea56aaa079a3
Create Date: 2024-02-04 21:27:35.797646

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '49fb10d64fa8'
down_revision: Union[str, None] = 'ea56aaa079a3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('accounts_inst', 'status')
    op.add_column('accounts_stories', sa.Column('aioscheduler_status', sa.Boolean(), nullable=False))
    op.add_column('accounts_stories', sa.Column('delay', sa.Integer(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('accounts_stories', 'delay')
    op.drop_column('accounts_stories', 'aioscheduler_status')
    op.add_column('accounts_inst', sa.Column('status', sa.BOOLEAN(), autoincrement=False, nullable=False))
    # ### end Alembic commands ###