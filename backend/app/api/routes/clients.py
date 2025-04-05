from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, Path, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from app.db.base import get_db
from app.models.client import Client
from app.models.policy import Policy
from app.models.conversation import Conversation
from app.models.document import Document
from app.schemas.client import ClientCreate, ClientUpdate, ClientList, ClientDetail
from app.core.exceptions import ResourceNotFoundException
from loguru import logger

router = APIRouter()

@router.get("/", response_model=List[ClientList])
async def get_clients(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    category: Optional[str] = None
):
    """
    Get list of clients with optional filtering
    """
    query = select(Client)
    
    # Apply filters if provided
    if search:
        query = query.filter(Client.name.ilike(f"%{search}%"))
    if category:
        query = query.filter(Client.category == category)
    
    # Apply pagination
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    clients = result.scalars().all()
    
    return clients

@router.post("/", response_model=ClientDetail, status_code=status.HTTP_201_CREATED)
async def create_client(
    client_in: ClientCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new client
    """
    client = Client(**client_in.model_dump())
    db.add(client)
    await db.commit()
    await db.refresh(client)
    
    return client

@router.get("/{client_id}", response_model=ClientDetail)
async def get_client(
    client_id: UUID = Path(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed information about a specific client
    """
    client = await db.get(Client, client_id)
    if not client:
        raise ResourceNotFoundException(f"Client with ID {client_id} not found")
    
    # Get associated counts
    policy_count_query = select(func.count(Policy.id)).where(Policy.client_id == client_id)
    conversation_count_query = select(func.count(Conversation.id)).where(Conversation.client_id == client_id)
    document_count_query = select(func.count(Document.id)).where(Document.client_id == client_id)
    
    policy_count_result = await db.execute(policy_count_query)
    conversation_count_result = await db.execute(conversation_count_query)
    document_count_result = await db.execute(document_count_query)
    
    policy_count = policy_count_result.scalar() or 0
    conversation_count = conversation_count_result.scalar() or 0
    document_count = document_count_result.scalar() or 0
    
    # Create response with counts
    response = ClientDetail(
        **client.__dict__,
        policy_count=policy_count,
        conversation_count=conversation_count,
        document_count=document_count
    )
    
    return response

@router.put("/{client_id}", response_model=ClientDetail)
async def update_client(
    client_update: ClientUpdate,
    client_id: UUID = Path(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Update client information
    """
    client = await db.get(Client, client_id)
    if not client:
        raise ResourceNotFoundException(f"Client with ID {client_id} not found")
    
    # Update client attributes if provided
    update_data = client_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(client, key, value)
    
    await db.commit()
    await db.refresh(client)
    
    # Get associated counts for response
    policy_count_query = select(func.count(Policy.id)).where(Policy.client_id == client_id)
    conversation_count_query = select(func.count(Conversation.id)).where(Conversation.client_id == client_id)
    document_count_query = select(func.count(Document.id)).where(Document.client_id == client_id)
    
    policy_count_result = await db.execute(policy_count_query)
    conversation_count_result = await db.execute(conversation_count_query)
    document_count_result = await db.execute(document_count_query)
    
    policy_count = policy_count_result.scalar() or 0
    conversation_count = conversation_count_result.scalar() or 0
    document_count = document_count_result.scalar() or 0
    
    # Create response with counts
    response = ClientDetail(
        **client.__dict__,
        policy_count=policy_count,
        conversation_count=conversation_count,
        document_count=document_count
    )
    
    return response

@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client(
    client_id: UUID = Path(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a client
    """
    client = await db.get(Client, client_id)
    if not client:
        raise ResourceNotFoundException(f"Client with ID {client_id} not found")
    
    await db.delete(client)
    await db.commit()
    
    return None 