from sqlalchemy import Column, String, ForeignKey, UUID, DateTime, Enum, JSON
from sqlalchemy.orm import relationship
from app.db.base import BaseModel

class Conversation(BaseModel):
    """
    Conversation model for client-advisor AI conversations
    """
    __tablename__ = "conversations"
    
    # Foreign key to Client
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id", ondelete="CASCADE"), nullable=False)
    
    # Conversation metadata
    function_type = Column(Enum("policy-explainer", "needs-assessment", "product-recommendation", "compliance-check", 
                                name="function_types"), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    
    # Conversation content
    messages = Column(JSON, nullable=False, default=list)
    
    # Relationship back to client
    client = relationship("Client", back_populates="conversations")
    
    def __repr__(self):
        return f"<Conversation {self.id} ({self.function_type}) for client {self.client_id}>" 