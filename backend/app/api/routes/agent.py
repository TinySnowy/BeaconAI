# backend/app/api/routes/agent.py
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

# Import the agent system
from app.agent.main import handle_agent_request

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
        
        # Process the query using the multi-agent system
        agent_result = await handle_agent_request(query_request, client, conversation)
        
        # Extract information from the agent result
        if agent_result["final_response"]:
            response_text = agent_result["final_response"]
        else:
            # Get the last AI message from the result
            for message in reversed(agent_result["messages"]):
                if isinstance(message, dict) and message.get("sender") == "ai":
                    response_text = message.get("content", "")
                    break
            else:
                # Fallback if no AI message found
                response_text = "The agent was unable to process your request."
        
        # Get the thinking process if available
        thinking = None
        for agent, output in agent_result["agent_outputs"].items():
            if agent != "coordinator" and "chain_of_thought" in output:
                thinking = output["chain_of_thought"]
                break
        
        # Get document references if available
        document_references = []
        for agent, output in agent_result["agent_outputs"].items():
            if agent != "coordinator" and "document_references" in output:
                for doc_ref in output["document_references"]:
                    document_references.append(DocumentReference(
                        id=UUID(doc_ref["id"]) if isinstance(doc_ref["id"], str) else doc_ref["id"],
                        title=doc_ref["title"],
                        type=doc_ref["type"],
                        snippet=doc_ref["snippet"]
                    ))
        
        # Create AI response message
        ai_message = {
            "id": str(uuid4()),
            "text": response_text,
            "sender": "ai",
            "timestamp": datetime.now().isoformat(),
            "agentType": query_request.function_type
        }
        
        # Add thinking process if available
        if thinking:
            ai_message["chainOfThought"] = thinking
        
        # Add document references if available
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
            detail=f"An error occurred while processing the query: {str(e)}"
        )
