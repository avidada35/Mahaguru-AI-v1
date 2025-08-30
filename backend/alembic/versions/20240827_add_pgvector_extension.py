"""Add pgvector extension

Revision ID: 20240827_add_pgvector_extension
Revises: 
Create Date: 2024-08-27 11:15:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20240827_add_pgvector_extension'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Enable the pgvector extension
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')
    
    # Add vector column to document_chunks table
    op.add_column('document_chunks', sa.Column('embedding', sa.dialects.postgresql.VECTOR(1536), nullable=True))
    
    # Create index for the embedding column
    op.create_index(
        'idx_document_chunks_embedding',
        'document_chunks',
        ['embedding'],
        postgresql_using='ivfflat',
        postgresql_with={'lists': 100},
        postgresql_ops={'embedding': 'vector_l2_ops'}
    )
    
    # Add other indexes for performance
    op.create_index('idx_document_chunks_document_id', 'document_chunks', ['document_id'])
    op.create_index('idx_document_chunks_user_id', 'document_chunks', ['user_id'])
    op.create_index('idx_document_chunks_created_at', 'document_chunks', ['created_at'])
    
    # Add language column
    op.add_column('document_chunks', sa.Column('language', sa.String(10), nullable=True))
    
    # Add metadata columns
    op.add_column('document_chunks', sa.Column('page_number', sa.Integer, nullable=True))
    op.add_column('document_chunks', sa.Column('section', sa.String(255), nullable=True))
    op.add_column('document_chunks', sa.Column('metadata', sa.JSON, nullable=True))

def downgrade():
    # Remove indexes
    op.drop_index('idx_document_chunks_embedding', table_name='document_chunks')
    op.drop_index('idx_document_chunks_document_id', table_name='document_chunks')
    op.drop_index('idx_document_chunks_user_id', table_name='document_chunks')
    op.drop_index('idx_document_chunks_created_at', table_name='document_chunks')
    
    # Remove columns
    op.drop_column('document_chunks', 'embedding')
    op.drop_column('document_chunks', 'language')
    op.drop_column('document_chunks', 'page_number')
    op.drop_column('document_chunks', 'section')
    op.drop_column('document_chunks', 'metadata')
    
    # Note: We don't drop the extension as it might be used by other databases
