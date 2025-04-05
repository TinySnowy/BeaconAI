from sqlalchemy import Column, String, Integer, Date, Enum
from sqlalchemy.orm import relationship
from app.db.base import BaseModel

class Client(BaseModel):
    """
    Client model representing insurance advisor's clients
    """
    __tablename__ = "clients"
    
    # Basic information
    name = Column(String, nullable=False, index=True)
    age = Column(Integer, nullable=False)
    occupation = Column(String, nullable=False)
    dependents = Column(Integer, default=0)
    
    # Contact information
    email = Column(String, unique=True, nullable=False)
    phone = Column(String, nullable=True)
    
    # Profile information
    risk_profile = Column(Enum("conservative", "moderate", "aggressive", name="risk_profile_types"), nullable=False)
    category = Column(Enum("active", "review", "pending", "prospect", name="client_categories"), nullable=False)
    next_review_date = Column(Date, nullable=True)
    
    # Relationships
    policies = relationship("Policy", back_populates="client", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="client", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="client", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Client {self.name} ({self.email})>" 