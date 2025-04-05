from uuid import UUID
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

# Base schema with common attributes
class DocumentBase(BaseModel):
    title: str = Field(..., description="Document title")
    type: str = Field(..., description="Document type", pattern="^(policy|financial|regulatory)$")
    content: str = Field(..., description="Document content")
    client_id: Optional[UUID] = Field(None, description="ID of the client associated with this document (optional)")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional document metadata")

# Schema for creating a new document
class DocumentCreate(DocumentBase):
    pass

# Schema for updating a document
class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    type: Optional[str] = Field(None, pattern="^(policy|financial|regulatory)$")
    content: Optional[str] = None
    client_id: Optional[UUID] = None
    metadata: Optional[Dict[str, Any]] = None

# Schema for returning document data
class DocumentInDB(DocumentBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Schema for document list response
class DocumentList(BaseModel):
    id: UUID
    title: str
    type: str
    client_id: Optional[UUID] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# Schema for document detail response
class DocumentDetail(DocumentInDB):
    client_name: Optional[str] = None
    
    class Config:
        from_attributes = True

# Schema for document search results
class DocumentSearchResult(BaseModel):
    id: UUID
    title: str
    type: str
    snippet: str
    client_id: Optional[UUID] = None
    client_name: Optional[str] = None
    relevance_score: float
    
    class Config:
        from_attributes = True 