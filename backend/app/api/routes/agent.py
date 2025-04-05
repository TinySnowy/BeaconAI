from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.base import get_db
from app.models.client import Client
from app.models.conversation import Conversation
from app.models.document import Document
from app.schemas.agent import (
    AgentQueryRequest, 
    AgentQueryResponse, 
    AgentErrorResponse, 
    DocumentReference,
    AgentStatus
)
from app.core.exceptions import ResourceNotFoundException
from loguru import logger

router = APIRouter()

@router.get("/status", response_model=AgentStatus)
async def get_agent_status(
    db: AsyncSession = Depends(get_db)
):
    """
    Get the current status of the agent system
    """
    # Count documents in the database
    document_count_query = select(Document)
    document_count_result = await db.execute(document_count_query)
    document_count = len(document_count_result.scalars().all())
    
    return {
        "status": "ready",
        "model_version": "0.1.0",
        "supported_functions": [
            "policy-explainer",
            "needs-assessment",
            "product-recommendation", 
            "compliance-check"
        ],
        "document_count": document_count
    }

@router.post("/query", response_model=AgentQueryResponse, responses={400: {"model": AgentErrorResponse}})
async def query_agent(
    query_request: AgentQueryRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Query the agent with a user message
    """
    try:
        # Validate client exists
        client = await db.get(Client, query_request.client_id)
        if not client:
            raise ResourceNotFoundException(f"Client with ID {query_request.client_id} not found")
        
        # Get or create conversation
        conversation = None
        if query_request.conversation_id:
            # Get existing conversation
            conversation = await db.get(Conversation, query_request.conversation_id)
            if not conversation:
                raise ResourceNotFoundException(f"Conversation with ID {query_request.conversation_id} not found")
            
            # Verify conversation belongs to the client
            if conversation.client_id != query_request.client_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Conversation does not belong to the specified client"
                )
            
            # Verify function type matches
            if conversation.function_type != query_request.function_type:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Function type does not match the conversation's function type"
                )
        else:
            # Create new conversation
            conversation = Conversation(
                client_id=query_request.client_id,
                function_type=query_request.function_type,
                timestamp=datetime.now(),
                messages=[]
            )
            db.add(conversation)
            await db.commit()
            await db.refresh(conversation)
        
        # Add user message to conversation
        user_message = {
            "id": str(uuid4()),
            "text": query_request.query,
            "sender": "user",
            "timestamp": datetime.now().isoformat()
        }
        
        if conversation.messages is None:
            conversation.messages = []
        
        conversation.messages.append(user_message)
        conversation.timestamp = datetime.now()
        
        # In a real implementation, this is where you would call the AI model
        # For now, we'll return a mock response
        
        # Mock document references
        document_references = []
        if query_request.function_type == "policy-explainer":
            # Find some policy documents to reference
            doc_query = select(Document).filter(
                Document.type == "policy", 
                Document.client_id == query_request.client_id
            ).limit(2)
            doc_result = await db.execute(doc_query)
            documents = doc_result.scalars().all()
            
            for doc in documents:
                document_references.append(DocumentReference(
                    id=doc.id,
                    title=doc.title,
                    type=doc.type,
                    snippet="This is a relevant excerpt from the document..."
                ))
        
        # Mock thinking process
        thinking = None
        if query_request.function_type == "needs-assessment":
            thinking = "1. Client profile indicates moderate risk tolerance\n2. Has dependents, so needs life coverage\n3. Age suggests retirement planning is important\n4. Current portfolio lacks health insurance"
        
        # Generate AI response based on function type
        response_text = ""
        if query_request.function_type == "policy-explainer":
            response_text = "Based on the client's policy documents, their current coverage includes term life insurance with $500,000 coverage until 2041. The policy includes standard exclusions for suicide within the first 2 years. Would you like me to explain any specific aspect of this policy in more detail?"
        elif query_request.function_type == "needs-assessment":
            response_text = "After analyzing the client's profile and current policies, I recommend focusing on health insurance coverage, which is currently missing from their portfolio. Given their age and dependents, this should be a priority alongside their existing life insurance."
        elif query_request.function_type == "product-recommendation":
            response_text = "For this client's needs, I would recommend our Premium Health Plan which provides comprehensive coverage with a moderate premium of $450/month. This would complement their existing term life policy and provide the health coverage they currently lack."
        elif query_request.function_type == "compliance-check":
            response_text = "The recommended product aligns with regulatory requirements. All necessary disclosures have been included in the documentation. You should ensure the client signs the risk disclosure form on page 3 before proceeding with the application."
        
        # Create AI response message
        ai_message = {
            "id": str(uuid4()),
            "text": response_text,
            "sender": "ai",
            "timestamp": datetime.now().isoformat(),
            "agentType": query_request.function_type
        }
        
        # Add any thinking or document references
        if thinking:
            ai_message["chainOfThought"] = thinking
        
        if document_references:
            ai_message["documentReferences"] = [
                {
                    "id": str(doc_ref.id),
                    "title": doc_ref.title,
                    "type": doc_ref.type,
                    "snippet": doc_ref.snippet
                } for doc_ref in document_references
            ]
        
        # Add AI message to conversation
        conversation.messages.append(ai_message)
        
        # Update conversation timestamp
        conversation.timestamp = datetime.now()
        
        # Save changes
        await db.commit()
        
        # Return response
        return {
            "conversation_id": conversation.id,
            "client_id": client.id,
            "function_type": query_request.function_type,
            "message": ai_message,
            "thinking": thinking,
            "document_references": document_references if document_references else None
        }
        
    except ResourceNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error in agent query: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing the query"
        ) 