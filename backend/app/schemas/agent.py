from uuid import UUID
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from app.schemas.conversation import Message

# Schema for Agent query request
class AgentQueryRequest(BaseModel):
    client_id: UUID = Field(..., description="ID of the client for this query")
    function_type: str = Field(..., description="Type of function to query", 
                              pattern="^(policy-explainer|needs-assessment|product-recommendation|compliance-check)$")
    query: str = Field(..., description="User query text")
    conversation_id: Optional[UUID] = Field(None, description="Existing conversation ID (if continuing a conversation)")

# Schema for document reference in agent response
class DocumentReference(BaseModel):
    id: UUID = Field(..., description="Document ID")
    title: str = Field(..., description="Document title")
    type: str = Field(..., description="Document type")
    snippet: str = Field(..., description="Relevant snippet from document")

# Schema for Agent query response
class AgentQueryResponse(BaseModel):
    conversation_id: UUID = Field(..., description="ID of the conversation (new or existing)")
    client_id: UUID = Field(..., description="ID of the client")
    function_type: str = Field(..., description="Type of function")
    message: Message = Field(..., description="AI response message")
    thinking: Optional[str] = Field(None, description="Agent's reasoning process (chain of thought)")
    document_references: Optional[List[DocumentReference]] = Field(None, description="Referenced documents")

# Schema for error response
class AgentErrorResponse(BaseModel):
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    
# Schema for agent system status
class AgentStatus(BaseModel):
    status: str = Field(..., description="Agent system status", pattern="^(ready|busy|error)$")
    model_version: str = Field(..., description="Current model version")
    supported_functions: List[str] = Field(..., description="List of supported function types")
    document_count: int = Field(..., description="Number of indexed documents") 