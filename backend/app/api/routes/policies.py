from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, Path, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from app.db.base import get_db
from app.models.policy import Policy
from app.models.client import Client
from app.schemas.policy import PolicyCreate, PolicyUpdate, PolicyList, PolicyDetail
from app.core.exceptions import ResourceNotFoundException
from loguru import logger

router = APIRouter()

@router.get("/", response_model=List[PolicyList])
async def get_policies(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    client_id: Optional[UUID] = None,
    policy_type: Optional[str] = None,
    status: Optional[str] = None
):
    """
    Get list of policies with optional filtering
    """
    query = select(Policy)
    
    # Apply filters if provided
    if client_id:
        query = query.filter(Policy.client_id == client_id)
    if policy_type:
        query = query.filter(Policy.type == policy_type)
    if status:
        query = query.filter(Policy.status == status)
    
    # Apply pagination
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    policies = result.scalars().all()
    
    return policies

@router.post("/", response_model=PolicyDetail, status_code=status.HTTP_201_CREATED)
async def create_policy(
    policy_in: PolicyCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new policy
    """
    # Check if client exists
    client = await db.get(Client, policy_in.client_id)
    if not client:
        raise ResourceNotFoundException(f"Client with ID {policy_in.client_id} not found")
    
    # Create policy
    policy = Policy(**policy_in.model_dump())
    db.add(policy)
    await db.commit()
    await db.refresh(policy)
    
    # Create response with client name
    response = PolicyDetail(
        **policy.__dict__,
        client_name=client.name
    )
    
    return response

@router.get("/{policy_id}", response_model=PolicyDetail)
async def get_policy(
    policy_id: UUID = Path(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed information about a specific policy
    """
    # Query for policy with joined client
    query = select(Policy).options(joinedload(Policy.client)).filter(Policy.id == policy_id)
    result = await db.execute(query)
    policy = result.scalars().first()
    
    if not policy:
        raise ResourceNotFoundException(f"Policy with ID {policy_id} not found")
    
    # Create response with client name
    response = PolicyDetail(
        **policy.__dict__,
        client_name=policy.client.name if policy.client else None
    )
    
    return response

@router.put("/{policy_id}", response_model=PolicyDetail)
async def update_policy(
    policy_update: PolicyUpdate,
    policy_id: UUID = Path(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Update policy information
    """
    # Query for policy with joined client
    query = select(Policy).options(joinedload(Policy.client)).filter(Policy.id == policy_id)
    result = await db.execute(query)
    policy = result.scalars().first()
    
    if not policy:
        raise ResourceNotFoundException(f"Policy with ID {policy_id} not found")
    
    # Update policy attributes if provided
    update_data = policy_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(policy, key, value)
    
    await db.commit()
    await db.refresh(policy)
    
    # Create response with client name
    response = PolicyDetail(
        **policy.__dict__,
        client_name=policy.client.name if policy.client else None
    )
    
    return response

@router.delete("/{policy_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_policy(
    policy_id: UUID = Path(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a policy
    """
    policy = await db.get(Policy, policy_id)
    if not policy:
        raise ResourceNotFoundException(f"Policy with ID {policy_id} not found")
    
    await db.delete(policy)
    await db.commit()
    
    return None 