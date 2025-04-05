import asyncio
from datetime import datetime, timedelta
import json
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.base import engine, Base, async_session
from app.models.client import Client
from app.models.policy import Policy
from app.models.conversation import Conversation
from app.models.document import Document
from sqlalchemy import text
from app.core.config import settings

# Sample data for initial database setup
SAMPLE_CLIENTS = [
    {
        "name": "John Smith",
        "age": 35,
        "occupation": "Software Engineer",
        "dependents": 2,
        "email": "john.smith@example.com",
        "phone": "+1-555-123-4567",
        "risk_profile": "moderate",
        "category": "active",
        "next_review_date": (datetime.now() + timedelta(days=30)).date()
    },
    {
        "name": "Sarah Johnson",
        "age": 42,
        "occupation": "Marketing Manager",
        "dependents": 1,
        "email": "sarah.johnson@example.com",
        "phone": "+1-555-987-6543",
        "risk_profile": "conservative",
        "category": "active",
        "next_review_date": (datetime.now() + timedelta(days=45)).date()
    },
    {
        "name": "Michael Brown",
        "age": 29,
        "occupation": "Teacher",
        "dependents": 0,
        "email": "michael.brown@example.com",
        "phone": "+1-555-456-7890",
        "risk_profile": "aggressive",
        "category": "pending",
        "next_review_date": None
    },
    {
        "name": "Emily Davis",
        "age": 55,
        "occupation": "Doctor",
        "dependents": 3,
        "email": "emily.davis@example.com",
        "phone": "+1-555-234-5678",
        "risk_profile": "conservative",
        "category": "review",
        "next_review_date": (datetime.now() + timedelta(days=15)).date()
    }
]

SAMPLE_POLICIES = [
    {
        "client_index": 0,  # John Smith
        "type": "term_life",
        "name": "Term Life 20",
        "premium": 1200.00,
        "coverage_amount": 500000.00,
        "start_date": (datetime.now() - timedelta(days=365)).date(),
        "end_date": (datetime.now() + timedelta(days=365 * 19)).date(),  # 20 year term
        "status": "active"
    },
    {
        "client_index": 0,  # John Smith
        "type": "health",
        "name": "Premium Health Plan",
        "premium": 450.00,
        "coverage_amount": 100000.00,
        "start_date": (datetime.now() - timedelta(days=180)).date(),
        "end_date": (datetime.now() + timedelta(days=185)).date(),  # 1 year term
        "status": "active"
    },
    {
        "client_index": 1,  # Sarah Johnson
        "type": "whole_life",
        "name": "Whole Life Plan",
        "premium": 350.00,
        "coverage_amount": 250000.00,
        "start_date": (datetime.now() - timedelta(days=730)).date(),  # 2 years ago
        "end_date": None,  # No end date for whole life
        "status": "active"
    },
    {
        "client_index": 2,  # Michael Brown
        "type": "health",
        "name": "Basic Health Plan",
        "premium": 200.00,
        "coverage_amount": 50000.00,
        "start_date": (datetime.now() - timedelta(days=90)).date(),
        "end_date": (datetime.now() + timedelta(days=275)).date(),  # 1 year term
        "status": "active"
    },
    {
        "client_index": 3,  # Emily Davis
        "type": "term_life",
        "name": "Term Life 15",
        "premium": 1500.00,
        "coverage_amount": 750000.00,
        "start_date": (datetime.now() - timedelta(days=1095)).date(),  # 3 years ago
        "end_date": (datetime.now() + timedelta(days=365 * 12)).date(),  # 15 year term
        "status": "active"
    },
    {
        "client_index": 3,  # Emily Davis
        "type": "investment",
        "name": "Investment-Linked Policy",
        "premium": 500.00,
        "coverage_amount": 100000.00,
        "start_date": (datetime.now() - timedelta(days=365)).date(),
        "end_date": None,  # No end date for ILP
        "status": "active"
    },
    {
        "client_index": 3,  # Emily Davis
        "type": "critical_illness",
        "name": "Critical Illness Cover",
        "premium": 300.00,
        "coverage_amount": 200000.00,
        "start_date": (datetime.now() - timedelta(days=180)).date(),
        "end_date": (datetime.now() + timedelta(days=185)).date(),  # 1 year term
        "status": "active"
    }
]

SAMPLE_CONVERSATIONS = [
    {
        "client_index": 0,  # John Smith
        "function_type": "policy-explainer",
        "timestamp": datetime.now() - timedelta(days=5),
        "messages": [
            {
                "id": "1",
                "text": "Hi, I need to review John Smith's life insurance policy. What can you tell me about his current coverage?",
                "sender": "user",
                "timestamp": (datetime.now() - timedelta(days=5)).isoformat()
            },
            {
                "id": "2",
                "text": "Based on John Smith's profile, he currently has a Term Life Insurance policy with the following details:\n\n- Coverage: $500,000\n- Term: 20 years\n- Premium: $1,200/year\n\nConsidering his family situation with 2 dependents, you should ensure his coverage is adequate. Would you like me to analyze if his current coverage amount is sufficient based on his financial needs?",
                "sender": "ai",
                "agentType": "policy-explainer",
                "timestamp": (datetime.now() - timedelta(days=5, minutes=-1)).isoformat(),
                "documentReferences": [
                    {
                        "id": "doc1",
                        "title": "Term Life Insurance Policy",
                        "type": "policy",
                        "snippet": "Coverage: $500,000 | Term: 20 years | Premium: $1,200/year"
                    }
                ]
            }
        ]
    },
    {
        "client_index": 1,  # Sarah Johnson
        "function_type": "needs-assessment",
        "timestamp": datetime.now() - timedelta(days=7),
        "messages": [
            {
                "id": "1",
                "text": "I'm meeting with Sarah Johnson next week to discuss her retirement planning options. What should I recommend?",
                "sender": "user",
                "timestamp": (datetime.now() - timedelta(days=7)).isoformat()
            },
            {
                "id": "2",
                "text": "For your upcoming meeting with Sarah Johnson, her current age of 42 makes this an ideal time to review retirement planning options.",
                "sender": "ai",
                "agentType": "needs-assessment",
                "timestamp": (datetime.now() - timedelta(days=7, minutes=-1)).isoformat(),
                "chainOfThought": "1. Client is 42 years old\n2. Retirement typically occurs between 60-65\n3. That gives approximately 18-23 years for retirement planning\n4. Client has one dependent, which affects financial planning\n5. Already has Whole Life Insurance with savings component\n6. Need to assess if additional retirement-specific products are needed"
            },
            {
                "id": "3",
                "text": "Sarah's current Whole Life Insurance policy provides a savings component, but you might want to discuss additional options like retirement-focused investment-linked policies or dedicated retirement plans. I can prepare a comparison of the key differences between these options for your meeting, highlighting the advantages of each based on her profile.",
                "sender": "ai",
                "agentType": "product-recommendation",
                "timestamp": (datetime.now() - timedelta(days=7, minutes=-2)).isoformat()
            }
        ]
    }
]

SAMPLE_DOCUMENTS = [
    {
        "title": "Term Life Insurance Policy - John Smith",
        "type": "policy",
        "content": """# Term Life Insurance Policy

**Policy Number:** TL-12345678
**Insured:** John Smith
**Coverage Amount:** $500,000
**Term:** 20 years
**Premium:** $1,200/year (paid annually)
**Issue Date:** March 15, 2021
**Expiry Date:** March 15, 2041

## Key Policy Provisions:

### 1. Death Benefit
The Company will pay the designated beneficiary the Coverage Amount upon receipt of proof that the insured died while this policy was in force.

### 2. Premium Payments
Premiums are payable annually on the policy anniversary date. A 30-day grace period is provided.

### 3. Beneficiary
Primary: Sarah Smith (Wife) - 100%
Contingent: Michael Smith (Son) - 50%, Emily Smith (Daughter) - 50%

### 4. Exclusions
- Suicide within first 2 years
- Material misrepresentation in application
- War or act of war

### 5. Conversion Option
This policy may be converted to a permanent life insurance policy without evidence of insurability before age 65 or the end of the term period, whichever comes first.

### 6. Renewability
This policy is renewable to age 80 at increased premiums without evidence of insurability.
""",
        "client_index": 0,  # John Smith
        "metadata": {
            "policy_number": "TL-12345678",
            "issue_date": "2021-03-15",
            "expiry_date": "2041-03-15"
        }
    },
    {
        "title": "Estate Planning Checklist",
        "type": "financial",
        "content": """# Estate Planning Checklist

## Essential Documents

1. **Will**
   - Designates executor
   - Names guardians for minor children
   - Specifies distribution of assets
   - Should be reviewed every 3-5 years

2. **Trust**
   - Revocable living trust to avoid probate
   - Special needs trust if applicable
   - Consider tax implications

3. **Power of Attorney**
   - Financial POA
   - Durable POA (remains in effect if incapacitated)
   - Limited vs. general POA

4. **Healthcare Directive**
   - Living will
   - Healthcare proxy designation
   - HIPAA authorization

5. **Beneficiary Designations**
   - Life insurance policies
   - Retirement accounts
   - Transfer-on-death accounts
   - Should be reviewed annually

## For High Net Worth Individuals

- Estate tax planning strategies
- Gifting strategies
- Charitable remainder trusts
- Life insurance trust
- Family limited partnerships
""",
        "client_index": 3,  # Emily Davis
        "metadata": {
            "created_date": datetime.now().isoformat(),
            "document_category": "financial_planning",
            "tags": ["estate", "planning", "checklist", "high_net_worth"]
        }
    },
    {
        "title": "MAS Notice FAA-N16",
        "type": "regulatory",
        "content": """# MAS Notice FAA-N16: Guidelines on Recommendations

## Introduction

This Notice is issued pursuant to section 58 of the Financial Advisers Act (Cap. 110) ["the Act"] and applies to all financial advisers.

## Guidelines on Fair Dealing with Clients

### 1. Know Your Client

Financial advisers should obtain sufficient information about a client's financial situation, personal needs, investment experience, risk appetite and capacity, and investment objectives.

### 2. Needs-Based Assessment

Financial advisers should conduct a proper analysis to determine if a product is suitable for a client based on:
- The client's financial objectives, risk tolerance, and financial situation.
- The product's risk characteristics, features, and limitations.
- Ensure that recommendations match the client's risk tolerance and financial needs.

### 3. Product Due Diligence

Financial advisers should:
- Conduct due diligence on all investment products they recommend.
- Understand the product's features, risks, benefits, and limitations.
- Assess the costs and fees associated with the product.

### 4. Disclosure Requirements

Financial advisers should clearly disclose:
- The nature and risks of the product.
- All fees, charges, and commissions.
- Any potential conflicts of interest.
- Any limitations of their advice.
""",
        "client_index": None,  # Not client-specific
        "metadata": {
            "regulatory_authority": "Monetary Authority of Singapore",
            "notice_number": "FAA-N16",
            "issue_date": "2018-04-23",
            "last_updated": "2021-06-15",
            "tags": ["compliance", "regulations", "recommendations", "financial_advice"]
        }
    }
]

async def init_pgvector(db_session: AsyncSession):
    """Initialize pgvector extension if it doesn't exist"""
    try:
        # Check if pgvector extension exists
        query = text("SELECT * FROM pg_extension WHERE extname = 'vector'")
        result = await db_session.execute(query)
        extension_exists = result.fetchone() is not None
        
        if not extension_exists:
            # Create the extension
            await db_session.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            await db_session.commit()
            logger.info("Created pgvector extension")
        else:
            logger.info("pgvector extension already exists")
    except Exception as e:
        logger.error(f"Error initializing pgvector: {e}")
        await db_session.rollback()
        raise

async def create_tables():
    """Create all tables defined in the models"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Created database tables")

async def insert_sample_data():
    """Insert sample data into the database"""
    async with async_session() as session:
        # First, check if we already have data
        result = await session.execute(select(Client))
        if result.scalars().first() is not None:
            logger.info("Database already contains data, skipping sample data insertion")
            return
        
        # Initialize pgvector extension
        await init_pgvector(session)
        
        # Insert clients
        clients = []
        for client_data in SAMPLE_CLIENTS:
            client = Client(**client_data)
            session.add(client)
            clients.append(client)
        
        await session.commit()
        logger.info(f"Inserted {len(clients)} sample clients")
        
        # Insert policies
        for policy_data in SAMPLE_POLICIES:
            client_index = policy_data.pop("client_index")
            client = clients[client_index]
            policy = Policy(client_id=client.id, **policy_data)
            session.add(policy)
        
        await session.commit()
        logger.info(f"Inserted {len(SAMPLE_POLICIES)} sample policies")
        
        # Insert conversations
        for conversation_data in SAMPLE_CONVERSATIONS:
            client_index = conversation_data.pop("client_index")
            messages = conversation_data.pop("messages")
            client = clients[client_index]
            conversation = Conversation(
                client_id=client.id,
                messages=messages,
                **conversation_data
            )
            session.add(conversation)
        
        await session.commit()
        logger.info(f"Inserted {len(SAMPLE_CONVERSATIONS)} sample conversations")
        
        # Insert documents
        for document_data in SAMPLE_DOCUMENTS:
            client_index = document_data.pop("client_index")
            client_id = clients[client_index].id if client_index is not None else None
            document = Document(client_id=client_id, **document_data)
            session.add(document)
        
        await session.commit()
        logger.info(f"Inserted {len(SAMPLE_DOCUMENTS)} sample documents")

async def init_db():
    """Initialize database with tables and sample data"""
    # Create database tables
    logger.info("Creating database tables...")
    await create_tables()
    
    # Check if tables are empty, if so, insert sample data
    async with async_session() as db:
        # Check if clients table is empty
        result = await db.execute(select(Client))
        clients = result.scalars().all()
        
        if not clients:
            logger.info("Inserting sample data...")
            await insert_sample_data()
            logger.info("Sample data inserted successfully")
        else:
            logger.info("Database already contains data, skipping sample data insertion")

if __name__ == "__main__":
    asyncio.run(init_db()) 