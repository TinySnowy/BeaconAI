from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, Path, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from datetime import datetime
from app.db.base import get_db
from app.models.conversation import Conversation
from app.models.client import Client
from app.schemas.conversation import ConversationCreate, ConversationUpdate, ConversationList, ConversationDetail, MessageCreate
from app.core.exceptions import ResourceNotFoundException
from loguru import logger

router = APIRouter()

@router.get("/", response_model=List[ConversationList])
async def get_conversations(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    client_id: Optional[UUID] = None,
    function_type: Optional[str] = None
):
    """
    Get list of conversations with optional filtering
    """
    query = select(Conversation)
    
    # Apply filters if provided
    if client_id:
        query = query.filter(Conversation.client_id == client_id)
    if function_type:
        query = query.filter(Conversation.function_type == function_type)
    
    # Apply pagination
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    conversations = result.scalars().all()
    
    # Calculate message count for each conversation
    conversation_list = []
    for conversation in conversations:
        message_count = len(conversation.messages)
        conversation_dict = {
            "id": conversation.id,
            "client_id": conversation.client_id,
            "function_type": conversation.function_type,
            "timestamp": conversation.timestamp,
            "message_count": message_count
        }
        conversation_list.append(conversation_dict)
    
    return conversation_list

@router.post("/", response_model=ConversationDetail, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    conversation_in: ConversationCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new conversation
    """
    # Check if client exists
    client = await db.get(Client, conversation_in.client_id)
    if not client:
        raise ResourceNotFoundException(f"Client with ID {conversation_in.client_id} not found")
    
    # Create conversation
    conversation = Conversation(**conversation_in.model_dump())
    db.add(conversation)
    await db.commit()
    await db.refresh(conversation)
    
    # Create response with client name
    response = ConversationDetail(
        **conversation.__dict__,
        client_name=client.name
    )
    
    return response

@router.get("/{conversation_id}", response_model=ConversationDetail)
async def get_conversation(
    conversation_id: UUID = Path(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed information about a specific conversation
    """
    # Query for conversation with joined client
    query = select(Conversation).options(joinedload(Conversation.client)).filter(Conversation.id == conversation_id)
    result = await db.execute(query)
    conversation = result.scalars().first()
    
    if not conversation:
        raise ResourceNotFoundException(f"Conversation with ID {conversation_id} not found")
    
    # Create response with client name
    response = ConversationDetail(
        **conversation.__dict__,
        client_name=conversation.client.name if conversation.client else None
    )
    
    return response

@router.put("/{conversation_id}", response_model=ConversationDetail)
async def update_conversation(
    conversation_update: ConversationUpdate,
    conversation_id: UUID = Path(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Update conversation information
    """
    # Query for conversation with joined client
    query = select(Conversation).options(joinedload(Conversation.client)).filter(Conversation.id == conversation_id)
    result = await db.execute(query)
    conversation = result.scalars().first()
    
    if not conversation:
        raise ResourceNotFoundException(f"Conversation with ID {conversation_id} not found")
    
    # Update conversation attributes if provided
    update_data = conversation_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(conversation, key, value)
    
    await db.commit()
    await db.refresh(conversation)
    
    # Create response with client name
    response = ConversationDetail(
        **conversation.__dict__,
        client_name=conversation.client.name if conversation.client else None
    )
    
    return response

@router.post("/{conversation_id}/messages", response_model=ConversationDetail)
async def add_message(
    message: MessageCreate,
    conversation_id: UUID = Path(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Add a new message to an existing conversation
    """
    # Query for conversation with joined client
    query = select(Conversation).options(joinedload(Conversation.client)).filter(Conversation.id == conversation_id)
    result = await db.execute(query)
    conversation = result.scalars().first()
    
    if not conversation:
        raise ResourceNotFoundException(f"Conversation with ID {conversation_id} not found")
    
    # Create new message
    new_message = {
        "id": str(UUID()),
        "text": message.text,
        "sender": message.sender,
        "timestamp": datetime.now().isoformat()
    }
    
    # Add message to conversation
    if conversation.messages is None:
        conversation.messages = []
    
    conversation.messages.append(new_message)
    conversation.timestamp = datetime.now()
    
    await db.commit()
    await db.refresh(conversation)
    
    # Create response with client name
    response = ConversationDetail(
        **conversation.__dict__,
        client_name=conversation.client.name if conversation.client else None
    )
    
    return response

@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: UUID = Path(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a conversation
    """
    conversation = await db.get(Conversation, conversation_id)
    if not conversation:
        raise ResourceNotFoundException(f"Conversation with ID {conversation_id} not found")
    
    await db.delete(conversation)
    await db.commit()
    
    return None 