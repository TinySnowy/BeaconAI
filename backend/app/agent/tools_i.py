# backend/app/agent/tools.py
from typing import List, Dict, Any, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.base import get_db
from app.models.document import Document
from app.models.client import Client
from app.models.policy import Policy
from loguru import logger

# Document Retrieval Tool
async def document_retrieval_tool(
    query: str,
    client_id: Optional[UUID] = None,
    document_type: Optional[str] = None,
    limit: int = 5,
    db: AsyncSession = None
) -> List[Dict[str, Any]]:
    """
    Retrieve relevant documents from the database based on query and filters
    
    Args:
        query: The search query
        client_id: Optional client ID to filter documents
        document_type: Optional document type to filter
        limit: Maximum number of documents to return
        db: Database session
    
    Returns:
        List of matching documents
    """
    if db is None:
        # This will need to be handled differently in an async context
        # For simplicity, we'll assume db is provided
        logger.error("Database session required for document retrieval")
        return []
    
    try:
        # In a production environment, use pgvector for semantic search
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
        return [
            {
                "id": doc.id,
                "title": doc.title,
                "type": doc.type,
                "content": doc.content,
                "client_id": doc.client_id,
                "metadata": doc.metadata
            }
            for doc in documents
        ]
    
    except Exception as e:
        logger.error(f"Error in document retrieval: {str(e)}")
        return []

# Client Database Tool
async def client_db_tool(
    client_id: UUID,
    db: AsyncSession = None
) -> Dict[str, Any]:
    """
    Retrieve client information and related data
    
    Args:
        client_id: The client ID
        db: Database session
    
    Returns:
        Client data with related information
    """
    if db is None:
        logger.error("Database session required for client lookup")
        return {}
    
    try:
        # Query for the client
        client = await db.get(Client, client_id)
        if not client:
            logger.error(f"Client with ID {client_id} not found")
            return {}
        
        # Query for client's policies
        policies_query = select(Policy).filter(Policy.client_id == client_id)
        policies_result = await db.execute(policies_query)
        policies = policies_result.scalars().all()
        
        # Build client profile
        return {
            "id": client.id,
            "name": client.name,
            "age": client.age,
            "occupation": client.occupation,
            "dependents": client.dependents,
            "email": client.email,
            "phone": client.phone,
            "risk_profile": client.risk_profile,
            "category": client.category,
            "next_review_date": client.next_review_date.isoformat() if client.next_review_date else None,
            "policies": [
                {
                    "id": policy.id,
                    "type": policy.type,
                    "name": policy.name,
                    "premium": policy.premium,
                    "coverage_amount": policy.coverage_amount,
                    "start_date": policy.start_date.isoformat(),
                    "end_date": policy.end_date.isoformat() if policy.end_date else None,
                    "status": policy.status
                }
                for policy in policies
            ]
        }
    
    except Exception as e:
        logger.error(f"Error in client database tool: {str(e)}")
        return {}

# Product Database Tool
async def product_db_tool(
    query: str = None,
    product_type: str = None,
    db: AsyncSession = None
) -> List[Dict[str, Any]]:
    """
    Search for insurance products in the database
    
    Args:
        query: Optional search query
        product_type: Optional product type filter
        db: Database session
    
    Returns:
        List of matching products
    """
    # Note: For the hackathon, you might want to use a hardcoded list of products
    # or create a separate products table in your database
    
    # Sample product data
    SAMPLE_PRODUCTS = [
        {
            "id": "prod-1",
            "name": "Term Life 20",
            "type": "term_life",
            "description": "20-year term life insurance policy with fixed premiums",
            "features": [
                "Fixed premium for 20 years",
                "Renewal option at end of term",
                "Conversion option to permanent life insurance"
            ],
            "min_coverage": 100000,
            "max_coverage": 5000000,
            "min_age": 18,
            "max_age": 65
        },
        {
            "id": "prod-2",
            "name": "Whole Life Plus",
            "type": "whole_life",
            "description": "Permanent life insurance with cash value accumulation",
            "features": [
                "Lifelong coverage",
                "Cash value growth",
                "Dividend potential",
                "Loan option against cash value"
            ],
            "min_coverage": 50000,
            "max_coverage": 2000000,
            "min_age": 18,
            "max_age": 70
        },
        {
            "id": "prod-3",
            "name": "Premium Health Plan",
            "type": "health",
            "description": "Comprehensive health insurance with hospital and outpatient coverage",
            "features": [
                "Hospitalization coverage",
                "Surgical benefits",
                "Outpatient treatment",
                "Specialist consultation"
            ],
            "min_coverage": 50000,
            "max_coverage": 1000000,
            "min_age": 18,
            "max_age": 75
        }
    ]
    
    # Filter products based on query and type
    filtered_products = SAMPLE_PRODUCTS
    
    if product_type:
        filtered_products = [p for p in filtered_products if p["type"] == product_type]
    
    if query:
        query_lower = query.lower()
        filtered_products = [
            p for p in filtered_products 
            if query_lower in p["name"].lower() or query_lower in p["description"].lower()
        ]
    
    return filtered_products

# Compliance Rules Tool
async def compliance_rules_tool(
    query: str = None,
    rule_type: str = None,
    db: AsyncSession = None
) -> List[Dict[str, Any]]:
    """
    Retrieve relevant compliance rules
    
    Args:
        query: Optional search query
        rule_type: Optional rule type filter
        db: Database session
    
    Returns:
        List of matching compliance rules
    """
    # Sample compliance rules
    SAMPLE_COMPLIANCE_RULES = [
        {
            "id": "rule-1",
            "title": "MAS Notice FAA-N16: Guidelines on Recommendations",
            "type": "regulatory",
            "description": "Financial advisers should recommend suitable products to clients based on their needs, objectives, and financial situation.",
            "requirements": [
                "Document client's financial objectives, risk tolerance, and financial situation",
                "Ensure products recommended match client's risk profile",
                "Disclose all fees, charges, and risks clearly",
                "Maintain proper documentation of advice given"
            ]
        },
        {
            "id": "rule-2",
            "title": "FAIR Principles",
            "type": "regulatory",
            "description": "Financial advisers should act in the best interest of the client, adhere to clear and transparent disclosure, and ensure recommendations are suitable.",
            "requirements": [
                "Act in client's best interest at all times",
                "Provide clear and transparent fee disclosure",
                "Ensure suitability of recommendations",
                "Maintain confidentiality of client information"
            ]
        },
        {
            "id": "rule-3",
            "title": "Investment-Linked Policy Disclosure",
            "type": "internal",
            "description": "Company policy on ILP disclosure requirements",
            "requirements": [
                "Explain that ILPs are investment products with insurance coverage",
                "Disclose that investment returns are not guaranteed",
                "Highlight potential risks and market volatility",
                "Explain all fees and charges including fund management fees"
            ]
        }
    ]
    
    # Filter rules based on query and type
    filtered_rules = SAMPLE_COMPLIANCE_RULES
    
    if rule_type:
        filtered_rules = [r for r in filtered_rules if r["type"] == rule_type]
    
    if query:
        query_lower = query.lower()
        filtered_rules = [
            r for r in filtered_rules 
            if query_lower in r["title"].lower() or query_lower in r["description"].lower()
        ]
    
    return filtered_rules

# Market Data Tool
async def market_data_tool(
    fund_name: str = None,
    time_period: str = "1y",
    db: AsyncSession = None
) -> Dict[str, Any]:
    """
    Retrieve market data for investment-linked policies
    
    Args:
        fund_name: Optional fund name to filter
        time_period: Time period for performance data (1m, 3m, 6m, 1y, 3y, 5y)
        db: Database session
    
    Returns:
        Market data for the specified fund
    """
    # Sample market data for ILP funds
    SAMPLE_FUND_DATA = {
        "Global Growth Fund": {
            "fund_name": "Global Growth Fund",
            "risk_rating": "Moderate",
            "inception_date": "2010-01-15",
            "fund_manager": "Jane Williams",
            "performance": {
                "1m": 1.2,
                "3m": 3.5,
                "6m": 5.8,
                "1y": 8.5,
                "3y": 23.4,
                "5y": 42.1
            },
            "allocation": {
                "Equities": 65,
                "Bonds": 20,
                "Cash": 10,
                "Others": 5
            },
            "top_holdings": [
                {"name": "Apple Inc.", "percentage": 3.5},
                {"name": "Microsoft Corp.", "percentage": 3.2},
                {"name": "Amazon.com Inc.", "percentage": 2.8},
                {"name": "Alphabet Inc.", "percentage": 2.5},
                {"name": "Taiwan Semiconductor", "percentage": 2.0}
            ]
        },
        "Income Plus Fund": {
            "fund_name": "Income Plus Fund",
            "risk_rating": "Conservative",
            "inception_date": "2012-03-20",
            "fund_manager": "Robert Chen",
            "performance": {
                "1m": 0.8,
                "3m": 2.1,
                "6m": 3.5,
                "1y": 5.2,
                "3y": 14.8,
                "5y": 25.3
            },
            "allocation": {
                "Equities": 30,
                "Bonds": 50,
                "Cash": 15,
                "Others": 5
            },
            "top_holdings": [
                {"name": "US Treasury 10Y", "percentage": 5.5},
                {"name": "JP Morgan Corp Bond ETF", "percentage": 4.8},
                {"name": "Johnson & Johnson", "percentage": 2.5},
                {"name": "Procter & Gamble", "percentage": 2.2},
                {"name": "Nestle S.A.", "percentage": 2.0}
            ]
        }
    }
    
    if fund_name and fund_name in SAMPLE_FUND_DATA:
        return SAMPLE_FUND_DATA[fund_name]
    elif fund_name:
        # Return empty data if fund not found
        return {"error": f"Fund '{fund_name}' not found"}
    else:
        # Return summary of all funds
        return {
            "funds": [
                {
                    "fund_name": fund["fund_name"],
                    "risk_rating": fund["risk_rating"],
                    "performance_1y": fund["performance"]["1y"],
                    "performance_3y": fund["performance"]["3y"]
                }
                for fund in SAMPLE_FUND_DATA.values()
            ]
        }