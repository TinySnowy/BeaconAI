from uuid import UUID
from datetime import date
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field

# Base schema with common attributes
class ClientBase(BaseModel):
    name: str = Field(..., description="Full name of the client")
    age: int = Field(..., description="Age of the client", ge=18, le=120)
    occupation: str = Field(..., description="Client's occupation")
    dependents: int = Field(..., description="Number of dependents", ge=0)
    email: EmailStr = Field(..., description="Client's email address")
    phone: Optional[str] = Field(None, description="Client's phone number")
    risk_profile: str = Field(..., description="Client's risk tolerance", pattern="^(conservative|moderate|aggressive)$")
    category: str = Field(..., description="Client's category", pattern="^(active|review|pending|prospect)$")
    next_review_date: Optional[date] = Field(None, description="Date for next client review")

# Schema for creating a new client
class ClientCreate(ClientBase):
    pass

# Schema for updating a client
class ClientUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = Field(None, ge=18, le=120)
    occupation: Optional[str] = None
    dependents: Optional[int] = Field(None, ge=0)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    risk_profile: Optional[str] = Field(None, pattern="^(conservative|moderate|aggressive)$")
    category: Optional[str] = Field(None, pattern="^(active|review|pending|prospect)$")
    next_review_date: Optional[date] = None

# Schema for returning client data
class ClientInDB(ClientBase):
    id: UUID
    created_at: date
    updated_at: date
    
    class Config:
        from_attributes = True

# Schema for client list response
class ClientList(BaseModel):
    id: UUID
    name: str
    age: int
    category: str
    risk_profile: str
    next_review_date: Optional[date] = None
    
    class Config:
        from_attributes = True

# Schema for detailed client response including counts
class ClientDetail(ClientInDB):
    policy_count: int = 0
    conversation_count: int = 0
    document_count: int = 0
    
    class Config:
        from_attributes = True 