from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, Path, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from app.db.base import get_db
from app.models.document import Document
from app.models.client import Client
from app.schemas.document import DocumentCreate, DocumentUpdate, DocumentList, DocumentDetail, DocumentSearchResult
from app.core.exceptions import ResourceNotFoundException
from loguru import logger

router = APIRouter()

@router.get("/", response_model=List[DocumentList])
async def get_documents(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    client_id: Optional[UUID] = None,
    document_type: Optional[str] = None
):
    """
    Get list of documents with optional filtering
    """
    query = select(Document)
    
    # Apply filters if provided
    if client_id:
        query = query.filter(Document.client_id == client_id)
    if document_type:
        query = query.filter(Document.type == document_type)
    
    # Apply pagination
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    documents = result.scalars().all()
    
    return documents

@router.post("/", response_model=DocumentDetail, status_code=status.HTTP_201_CREATED)
async def create_document(
    document_in: DocumentCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new document
    """
    # Check if client exists (if client_id provided)
    client_name = None
    if document_in.client_id:
        client = await db.get(Client, document_in.client_id)
        if not client:
            raise ResourceNotFoundException(f"Client with ID {document_in.client_id} not found")
        client_name = client.name
    
    # Create document
    document = Document(**document_in.model_dump())
    db.add(document)
    await db.commit()
    await db.refresh(document)
    
    # Create response with client name
    response = DocumentDetail(
        **document.__dict__,
        client_name=client_name
    )
    
    return response

@router.get("/{document_id}", response_model=DocumentDetail)
async def get_document(
    document_id: UUID = Path(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed information about a specific document
    """
    # Query for document with joined client
    query = select(Document).options(joinedload(Document.client)).filter(Document.id == document_id)
    result = await db.execute(query)
    document = result.scalars().first()
    
    if not document:
        raise ResourceNotFoundException(f"Document with ID {document_id} not found")
    
    # Create response with client name
    response = DocumentDetail(
        **document.__dict__,
        client_name=document.client.name if document.client else None
    )
    
    return response

@router.put("/{document_id}", response_model=DocumentDetail)
async def update_document(
    document_update: DocumentUpdate,
    document_id: UUID = Path(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Update document information
    """
    # Query for document with joined client
    query = select(Document).options(joinedload(Document.client)).filter(Document.id == document_id)
    result = await db.execute(query)
    document = result.scalars().first()
    
    if not document:
        raise ResourceNotFoundException(f"Document with ID {document_id} not found")
    
    # Check if client exists (if client_id provided in update)
    update_data = document_update.model_dump(exclude_unset=True)
    if 'client_id' in update_data and update_data['client_id'] is not None:
        client = await db.get(Client, update_data['client_id'])
        if not client:
            raise ResourceNotFoundException(f"Client with ID {update_data['client_id']} not found")
    
    # Update document attributes
    for key, value in update_data.items():
        setattr(document, key, value)
    
    await db.commit()
    await db.refresh(document)
    
    # Create response with client name
    client_name = None
    if document.client_id:
        client_query = select(Client).filter(Client.id == document.client_id)
        client_result = await db.execute(client_query)
        client = client_result.scalars().first()
        if client:
            client_name = client.name
    
    response = DocumentDetail(
        **document.__dict__,
        client_name=client_name
    )
    
    return response

@router.get("/search/", response_model=List[DocumentSearchResult])
async def search_documents(
    query: str = Query(..., min_length=3),
    client_id: Optional[UUID] = None,
    document_type: Optional[str] = None,
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """
    Search documents based on content (placeholder for semantic search)
    This is a basic implementation that will be replaced with pgvector search
    """
    # For now, we'll do a simple ILIKE search
    search_query = select(Document).where(Document.content.ilike(f"%{query}%"))
    
    # Apply filters if provided
    if client_id:
        search_query = search_query.filter(Document.client_id == client_id)
    if document_type:
        search_query = search_query.filter(Document.type == document_type)
    
    # Limit results
    search_query = search_query.limit(limit)
    
    # Execute query
    result = await db.execute(search_query)
    documents = result.scalars().all()
    
    # Format results
    search_results = []
    for doc in documents:
        # Extract snippet around the query term (simplistic approach)
        content = doc.content
        query_pos = content.lower().find(query.lower())
        start = max(0, query_pos - 50)
        end = min(len(content), query_pos + len(query) + 50)
        snippet = content[start:end]
        
        # Get client name if applicable
        client_name = None
        if doc.client_id:
            client_query = select(Client).filter(Client.id == doc.client_id)
            client_result = await db.execute(client_query)
            client = client_result.scalars().first()
            if client:
                client_name = client.name
        
        # Add to results
        search_results.append({
            "id": doc.id,
            "title": doc.title,
            "type": doc.type,
            "snippet": f"...{snippet}..." if query_pos >= 0 else snippet,
            "client_id": doc.client_id,
            "client_name": client_name,
            "relevance_score": 1.0  # Placeholder for real relevance score
        })
    
    return search_results

@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: UUID = Path(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a document
    """
    document = await db.get(Document, document_id)
    if not document:
        raise ResourceNotFoundException(f"Document with ID {document_id} not found")
    
    await db.delete(document)
    await db.commit()
    
    return None 