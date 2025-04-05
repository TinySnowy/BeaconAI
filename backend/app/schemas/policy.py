from uuid import UUID
from datetime import date
from typing import Optional
from pydantic import BaseModel, Field

# Base schema with common attributes
class PolicyBase(BaseModel):
    type: str = Field(..., description="Type of policy", pattern="^(term_life|whole_life|health|critical_illness|investment|general|retirement)$")
    name: str = Field(..., description="Name of the policy")
    premium: float = Field(..., description="Premium amount", gt=0)
    coverage_amount: float = Field(..., description="Coverage amount", gt=0)
    start_date: date = Field(..., description="Policy start date")
    end_date: Optional[date] = Field(None, description="Policy end date (null for permanent policies)")
    status: str = Field(..., description="Policy status", pattern="^(active|lapsed|pending|cancelled)$")

# Schema for creating a new policy
class PolicyCreate(PolicyBase):
    client_id: UUID = Field(..., description="ID of the client who owns the policy")

# Schema for updating a policy
class PolicyUpdate(BaseModel):
    type: Optional[str] = Field(None, pattern="^(term_life|whole_life|health|critical_illness|investment|general|retirement)$")
    name: Optional[str] = None
    premium: Optional[float] = Field(None, gt=0)
    coverage_amount: Optional[float] = Field(None, gt=0)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[str] = Field(None, pattern="^(active|lapsed|pending|cancelled)$")

# Schema for returning policy data
class PolicyInDB(PolicyBase):
    id: UUID
    client_id: UUID
    created_at: date
    updated_at: date
    
    class Config:
        from_attributes = True

# Schema for policy list response
class PolicyList(BaseModel):
    id: UUID
    client_id: UUID
    name: str
    type: str
    premium: float
    coverage_amount: float
    status: str
    start_date: date
    end_date: Optional[date] = None
    
    class Config:
        from_attributes = True

# Schema for policy detail response
class PolicyDetail(PolicyInDB):
    client_name: Optional[str] = None
    
    class Config:
        from_attributes = True 