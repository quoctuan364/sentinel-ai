"""Initial schema migration

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2026-10-10 14:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '0001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('email', sa.String(length=255), nullable=False, unique=True),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_users_email', 'users', ['email'])

    # Workspaces table
    op.create_table(
        'workspaces',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('slug', sa.String(length=255), nullable=False, unique=True),
        sa.Column('review_mode', sa.String(length=50), default='ADVISORY'),
        sa.Column('ai_monthly_budget_cents', sa.Integer(), default=5000),
        sa.Column('ai_used_cents', sa.Integer(), default=0),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_workspaces_slug', 'workspaces', ['slug'])

    # Workspace Memberships table
    op.create_table(
        'workspace_memberships',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('workspace_id', sa.String(length=36), sa.ForeignKey('workspaces.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', sa.String(length=36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('role', sa.String(length=50), default='DEVELOPER'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint('workspace_id', 'user_id', name='uq_workspace_user'),
    )

    # GitHub Installations table
    op.create_table(
        'github_installations',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('workspace_id', sa.String(length=36), sa.ForeignKey('workspaces.id', ondelete='CASCADE'), nullable=False),
        sa.Column('installation_id', sa.Integer(), nullable=False),
        sa.Column('account_login', sa.String(length=255), nullable=False),
        sa.Column('account_type', sa.String(length=50), default='Organization'),
        sa.Column('permissions', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )

    # Repositories table
    op.create_table(
        'repositories',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('workspace_id', sa.String(length=36), sa.ForeignKey('workspaces.id', ondelete='CASCADE'), nullable=False),
        sa.Column('github_installation_id', sa.String(length=36), sa.ForeignKey('github_installations.id', ondelete='SET NULL'), nullable=True),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('default_branch', sa.String(length=100), default='main'),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('scan_on_pr', sa.Boolean(), default=True),
        sa.Column('min_severity_for_review', sa.String(length=50), default='HIGH'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_repositories_full_name', 'repositories', ['full_name'])

    # Webhook Deliveries table
    op.create_table(
        'webhook_deliveries',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('delivery_id', sa.String(length=100), nullable=False, unique=True),
        sa.Column('event_type', sa.String(length=100), nullable=False),
        sa.Column('payload_hash', sa.String(length=64), nullable=False),
        sa.Column('status', sa.String(length=50), default='RECEIVED'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_webhook_deliveries_delivery_id', 'webhook_deliveries', ['delivery_id'])

    # Scan Jobs table
    op.create_table(
        'scan_jobs',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('workspace_id', sa.String(length=36), sa.ForeignKey('workspaces.id', ondelete='CASCADE'), nullable=False),
        sa.Column('repository_id', sa.String(length=36), sa.ForeignKey('repositories.id', ondelete='CASCADE'), nullable=False),
        sa.Column('pr_number', sa.Integer(), nullable=True),
        sa.Column('commit_sha', sa.String(length=64), nullable=False),
        sa.Column('branch_name', sa.String(length=255), default='main'),
        sa.Column('base_branch', sa.String(length=255), default='main'),
        sa.Column('title', sa.String(length=255), default='Security Scan'),
        sa.Column('trigger', sa.String(length=50), default='MANUAL'),
        sa.Column('status', sa.String(length=50), default='PENDING'),
        sa.Column('retry_count', sa.Integer(), default=0),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('duration_seconds', sa.Float(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('ai_triage_enabled', sa.Boolean(), default=True),
        sa.Column('ai_summary', sa.JSON(), nullable=True),
        sa.Column('sarif_report', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_scan_jobs_status', 'scan_jobs', ['status'])

    # Findings table
    op.create_table(
        'findings',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('scan_id', sa.String(length=36), sa.ForeignKey('scan_jobs.id', ondelete='CASCADE'), nullable=False),
        sa.Column('workspace_id', sa.String(length=36), sa.ForeignKey('workspaces.id', ondelete='CASCADE'), nullable=False),
        sa.Column('repository_id', sa.String(length=36), sa.ForeignKey('repositories.id', ondelete='CASCADE'), nullable=False),
        sa.Column('fingerprint', sa.String(length=64), nullable=False),
        sa.Column('scanner_name', sa.String(length=50), nullable=False),
        sa.Column('rule_id', sa.String(length=150), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('severity', sa.String(length=50), nullable=False),
        sa.Column('confidence', sa.String(length=50), default='HIGH'),
        sa.Column('cwe_id', sa.String(length=50), nullable=True),
        sa.Column('file_path', sa.String(length=500), nullable=False),
        sa.Column('start_line', sa.Integer(), default=1),
        sa.Column('end_line', sa.Integer(), default=1),
        sa.Column('code_snippet', sa.Text(), nullable=True),
        sa.Column('remediation_guidance', sa.Text(), nullable=True),
        sa.Column('validation_status', sa.String(length=50), default='CONFIRMED'),
        sa.Column('lifecycle_status', sa.String(length=50), default='OPEN'),
        sa.Column('ai_explanation', sa.Text(), nullable=True),
        sa.Column('ai_suggested_patch', sa.Text(), nullable=True),
        sa.Column('first_seen_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('last_seen_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_findings_fingerprint', 'findings', ['fingerprint'])
    op.create_index('ix_findings_severity', 'findings', ['severity'])

    # Finding Audits table
    op.create_table(
        'finding_audits',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('finding_id', sa.String(length=36), sa.ForeignKey('findings.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', sa.String(length=36), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('old_status', sa.String(length=50), nullable=False),
        sa.Column('new_status', sa.String(length=50), nullable=False),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )

    # AI Analysis Records table
    op.create_table(
        'ai_analysis_records',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('scan_id', sa.String(length=36), sa.ForeignKey('scan_jobs.id', ondelete='CASCADE'), nullable=False),
        sa.Column('workspace_id', sa.String(length=36), sa.ForeignKey('workspaces.id', ondelete='CASCADE'), nullable=False),
        sa.Column('provider', sa.String(length=50), nullable=False),
        sa.Column('model_name', sa.String(length=100), nullable=False),
        sa.Column('prompt_version', sa.String(length=50), default='v1.0'),
        sa.Column('input_tokens', sa.Integer(), default=0),
        sa.Column('output_tokens', sa.Integer(), default=0),
        sa.Column('duration_ms', sa.Integer(), default=0),
        sa.Column('status', sa.String(length=50), default='SUCCEEDED'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )

    # Usage Records table
    op.create_table(
        'usage_records',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('workspace_id', sa.String(length=36), sa.ForeignKey('workspaces.id', ondelete='CASCADE'), nullable=False),
        sa.Column('metric', sa.String(length=100), nullable=False),
        sa.Column('quantity', sa.Integer(), default=1),
        sa.Column('recorded_at', sa.DateTime(timezone=True), nullable=False),
    )

    # Audit Events table
    op.create_table(
        'audit_events',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('workspace_id', sa.String(length=36), sa.ForeignKey('workspaces.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', sa.String(length=36), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('resource_type', sa.String(length=100), nullable=False),
        sa.Column('resource_id', sa.String(length=100), nullable=True),
        sa.Column('details', sa.JSON(), nullable=True),
        sa.Column('ip_address', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('audit_events')
    op.drop_table('usage_records')
    op.drop_table('ai_analysis_records')
    op.drop_table('finding_audits')
    op.drop_table('findings')
    op.drop_table('scan_jobs')
    op.drop_table('webhook_deliveries')
    op.drop_table('repositories')
    op.drop_table('github_installations')
    op.drop_table('workspace_memberships')
    op.drop_table('workspaces')
    op.drop_table('users')
