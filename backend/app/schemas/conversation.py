from uuid import UUID
from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field

# Message schema for conversation
class Message(BaseModel):
    id: str
    text: str
    sender: str = Field(..., pattern="^(user|ai)$")
    timestamp: str
    agentType: Optional[str] = None
    chainOfThought: Optional[str] = None
    documentReferences: Optional[List[Dict[str, Any]]] = None

# New message schema
class MessageCreate(BaseModel):
    text: str = Field(..., description="Message text content")
    sender: str = Field(..., description="Message sender", pattern="^(user|ai)$")

# Base schema with common attributes
class ConversationBase(BaseModel):
    client_id: UUID = Field(..., description="ID of the client for this conversation")
    function_type: str = Field(..., description="Type of conversation function", 
                              pattern="^(policy-explainer|needs-assessment|product-recommendation|compliance-check)$")
    timestamp: datetime = Field(..., description="Timestamp of the conversation")

# Schema for creating a new conversation
class ConversationCreate(ConversationBase):
    messages: List[Message] = Field(default_factory=list, description="Initial messages for the conversation")

# Schema for updating a conversation
class ConversationUpdate(BaseModel):
    messages: Optional[List[Message]] = None
    timestamp: Optional[datetime] = None

# Schema for returning conversation data
class ConversationInDB(ConversationBase):
    id: UUID
    messages: List[Message]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Schema for conversation list response
class ConversationList(BaseModel):
    id: UUID
    client_id: UUID
    function_type: str
    timestamp: datetime
    message_count: int
    
    class Config:
        from_attributes = True

# Schema for conversation detail response
class ConversationDetail(ConversationInDB):
    client_name: Optional[str] = None
    
    class Config:
        from_attributes = True 