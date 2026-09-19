"""Initial users, analyses, metrics and audit schema."""
from alembic import op
import sqlalchemy as sa

revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('users',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('username', sa.String(50), nullable=False),
        sa.Column('email', sa.String(100), nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('role', sa.String(10), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False))
    op.create_index('ix_users_username', 'users', ['username'], unique=True)
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.create_table('analysis_records',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('file_name', sa.String(255), nullable=False),
        sa.Column('file_type', sa.String(10), nullable=False),
        sa.Column('file_url', sa.String(500), nullable=False),
        sa.Column('storage_path', sa.String(1000), nullable=False),
        sa.Column('analysis_type', sa.String(20), nullable=False),
        *[sa.Column('score_' + category, sa.Numeric(5, 2), nullable=True) for category in ('safe', 'explicit', 'suggestive', 'gore')],
        sa.Column('extracted_text', sa.Text(), nullable=True),
        sa.Column('text_flagged', sa.Boolean(), nullable=False),
        sa.Column('text_flag_reason', sa.String(255), nullable=True),
        sa.Column('vector_id', sa.String(64), nullable=True),
        sa.Column('is_duplicate', sa.Boolean(), nullable=False),
        sa.Column('matched_record_id', sa.String(36), nullable=True),
        sa.Column('similarity_score', sa.Numeric(5, 2), nullable=True),
        sa.Column('ai_explanation', sa.Text(), nullable=True),
        sa.Column('overall_status', sa.String(10), nullable=False),
        sa.Column('result', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False))
    for column in ('user_id', 'overall_status', 'created_at'):
        op.create_index('ix_analysis_records_' + column, 'analysis_records', [column])
    op.create_table('platform_metrics',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('metric_key', sa.String(50), nullable=False, unique=True),
        sa.Column('metric_value', sa.Integer(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False))
    op.create_table('audit_logs',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), nullable=True),
        sa.Column('action', sa.String(80), nullable=False),
        sa.Column('details', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False))


def downgrade():
    op.drop_table('audit_logs')
    op.drop_table('platform_metrics')
    op.drop_table('analysis_records')
    op.drop_table('users')
