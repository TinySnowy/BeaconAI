from sqlalchemy import Column, String, Text, ForeignKey, UUID, Enum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY, FLOAT
from app.db.base import BaseModel

class Document(BaseModel):
    """
    Document model for client-related documents like policies, financial reports, etc.
    Includes pgvector embeddings for semantic search
    """
    __tablename__ = "documents"
    
    # Document metadata
    title = Column(String, nullable=False)
    type = Column(Enum("policy", "financial", "regulatory", name="document_types"), nullable=False)
    
    # Document content
    content = Column(Text, nullable=False)
    
    # Foreign key to Client (optional, some documents may not be client-specific)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id", ondelete="SET NULL"), nullable=True)
    
    # Additional metadata stored as JSON
    metadata = Column(JSON, nullable=True)
    
    # Vector embedding for document content - using pgvector
    # 1536 dimensions for OpenAI embeddings or 384 for smaller models
    embedding_vector = Column(ARRAY(FLOAT), nullable=True)
    
    # Relationship back to client
    client = relationship("Client", back_populates="documents")
    
    def __repr__(self):
        return f"<Document {self.title} ({self.type})>" 