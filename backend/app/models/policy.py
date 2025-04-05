from sqlalchemy import Column, String, Float, Date, ForeignKey, Enum, UUID
from sqlalchemy.orm import relationship
from app.db.base import BaseModel

class Policy(BaseModel):
    """
    Policy model representing insurance policies associated with clients
    """
    __tablename__ = "policies"
    
    # Foreign key to Client
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id", ondelete="CASCADE"), nullable=False)
    
    # Policy details
    type = Column(Enum("term_life", "whole_life", "health", "critical_illness", "investment", "general", "retirement", name="policy_types"), nullable=False)
    name = Column(String, nullable=False)
    premium = Column(Float, nullable=False)
    coverage_amount = Column(Float, nullable=False)
    
    # Policy dates
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)  # Null for permanent policies like whole life
    
    # Policy status
    status = Column(Enum("active", "lapsed", "pending", "cancelled", name="policy_statuses"), nullable=False)
    
    # Relationship back to client
    client = relationship("Client", back_populates="policies")
    
    def __repr__(self):
        return f"<Policy {self.name} ({self.type}) for client {self.client_id}>" 