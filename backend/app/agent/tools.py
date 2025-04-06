# backend/app/agent/tools.py
from typing import List, Dict, Any, Optional
from uuid import UUID, uuid4
from datetime import datetime, date, timedelta
import json
from loguru import logger

# Mock data for clients
MOCK_CLIENTS = {
    "client-1": {
        "id": "client-1",
        "name": "John Smith",
        "age": 35,
        "occupation": "Software Engineer",
        "dependents": 2,
        "email": "john.smith@example.com",
        "phone": "+1-555-123-4567",
        "risk_profile": "moderate",
        "category": "active",
        "next_review_date": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    },
    "client-2": {
        "id": "client-2",
        "name": "Sarah Johnson",
        "age": 42,
        "occupation": "Marketing Manager",
        "dependents": 1,
        "email": "sarah.johnson@example.com",
        "phone": "+1-555-987-6543",
        "risk_profile": "conservative",
        "category": "active",
        "next_review_date": (datetime.now() + timedelta(days=45)).strftime("%Y-%m-%d")
    },
    "client-3": {
        "id": "client-3",
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
    "client-4": {
        "id": "client-4",
        "name": "Emily Davis",
        "age": 55,
        "occupation": "Doctor",
        "dependents": 3,
        "email": "emily.davis@example.com",
        "phone": "+1-555-234-5678",
        "risk_profile": "conservative",
        "category": "review",
        "next_review_date": (datetime.now() + timedelta(days=15)).strftime("%Y-%m-%d")
    }
}

# Mock data for policies
MOCK_POLICIES = {
    "policy-1": {
        "id": "policy-1",
        "client_id": "client-1",
        "type": "term_life",
        "name": "Term Life 20",
        "premium": 1200.00,
        "coverage_amount": 500000.00,
        "start_date": (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d"),
        "end_date": (datetime.now() + timedelta(days=365 * 19)).strftime("%Y-%m-%d"),
        "status": "active"
    },
    "policy-2": {
        "id": "policy-2",
        "client_id": "client-1",
        "type": "health",
        "name": "Premium Health Plan",
        "premium": 450.00,
        "coverage_amount": 100000.00,
        "start_date": (datetime.now() - timedelta(days=180)).strftime("%Y-%m-%d"),
        "end_date": (datetime.now() + timedelta(days=185)).strftime("%Y-%m-%d"),
        "status": "active"
    },
    "policy-3": {
        "id": "policy-3",
        "client_id": "client-2",
        "type": "whole_life",
        "name": "Whole Life Plan",
        "premium": 350.00,
        "coverage_amount": 250000.00,
        "start_date": (datetime.now() - timedelta(days=730)).strftime("%Y-%m-%d"),
        "end_date": None,
        "status": "active"
    },
    "policy-4": {
        "id": "policy-4",
        "client_id": "client-3",
        "type": "health",
        "name": "Basic Health Plan",
        "premium": 200.00,
        "coverage_amount": 50000.00,
        "start_date": (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d"),
        "end_date": (datetime.now() + timedelta(days=275)).strftime("%Y-%m-%d"),
        "status": "active"
    },
    "policy-5": {
        "id": "policy-5",
        "client_id": "client-4",
        "type": "term_life",
        "name": "Term Life 15",
        "premium": 1500.00,
        "coverage_amount": 750000.00,
        "start_date": (datetime.now() - timedelta(days=1095)).strftime("%Y-%m-%d"),
        "end_date": (datetime.now() + timedelta(days=365 * 12)).strftime("%Y-%m-%d"),
        "status": "active"
    },
    "policy-6": {
        "id": "policy-6",
        "client_id": "client-4",
        "type": "investment",
        "name": "Investment-Linked Policy",
        "premium": 500.00,
        "coverage_amount": 100000.00,
        "start_date": (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d"),
        "end_date": None,
        "status": "active"
    },
    "policy-7": {
        "id": "policy-7",
        "client_id": "client-4",
        "type": "critical_illness",
        "name": "Critical Illness Cover",
        "premium": 300.00,
        "coverage_amount": 200000.00,
        "start_date": (datetime.now() - timedelta(days=180)).strftime("%Y-%m-%d"),
        "end_date": (datetime.now() + timedelta(days=185)).strftime("%Y-%m-%d"),
        "status": "active"
    }
}

# Mock data for documents
MOCK_DOCUMENTS = {
    "doc-1": {
        "id": "doc-1",
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
        "client_id": "client-1",
        "metadata": {
            "policy_number": "TL-12345678",
            "issue_date": "2021-03-15",
            "expiry_date": "2041-03-15"
        }
    },
    "doc-2": {
        "id": "doc-2",
        "title": "Health Insurance Policy - John Smith",
        "type": "policy",
        "content": """# Health Insurance Policy

**Policy Number:** H-98765432
**Insured:** John Smith
**Type:** Comprehensive Health Insurance
**Annual Limit:** $100,000
**Deductible:** $1,000
**Premium:** $450/month
**Issue Date:** October 12, 2022
**Renewal Date:** October 12, 2023

## Coverage Details:

### 1. Hospitalization Benefits
- Room and board: Up to $300 per day
- Intensive Care Unit: Up to $600 per day
- Hospital miscellaneous services: Covered in full

### 2. Surgical Benefits
- Surgical fees: As per schedule, up to $50,000
- Anesthetist fees: Up to 30% of surgical fees
- Operating theater: Covered in full

### 3. Outpatient Benefits
- General practitioner consultation: Up to $100 per visit
- Specialist consultation: Up to $150 per visit
- Diagnostic procedures: Up to $3,000 per year

### 4. Exclusions
- Pre-existing conditions (unless declared and accepted)
- Cosmetic treatments or surgery
- Self-inflicted injuries
- Treatments for substance abuse
""",
        "client_id": "client-1",
        "metadata": {
            "policy_number": "H-98765432",
            "issue_date": "2022-10-12",
            "renewal_date": "2023-10-12"
        }
    },
    "doc-3": {
        "id": "doc-3",
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
""",
        "client_id": "client-4",
        "metadata": {
            "created_date": datetime.now().isoformat(),
            "document_category": "financial_planning",
            "tags": ["estate", "planning", "checklist", "high_net_worth"]
        }
    },
    "doc-4": {
        "id": "doc-4",
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
        "client_id": None,
        "metadata": {
            "regulatory_authority": "Monetary Authority of Singapore",
            "notice_number": "FAA-N16",
            "issue_date": "2018-04-23",
            "last_updated": "2021-06-15",
            "tags": ["compliance", "regulations", "recommendations", "financial_advice"]
        }
    },
    "doc-5": {
        "id": "doc-5",
        "title": "Global Growth Fund Performance Report",
        "type": "financial",
        "content": """# Global Growth Fund Performance Report

## Fund Overview
**Fund Name:** Global Growth Fund
**Inception Date:** January 15, 2010
**Fund Manager:** Jane Williams
**Risk Rating:** Moderate
**Investment Objective:** Long-term capital growth

## Performance Summary

| Period | Return | Benchmark | +/- Benchmark |
|--------|--------|-----------|---------------|
| 1 Year | 8.5%   | 7.2%      | +1.3%         |
| 3 Year | 23.4%  | 21.5%     | +1.9%         |
| 5 Year | 42.1%  | 38.5%     | +3.6%         |
| YTD    | 3.2%   | 2.9%      | +0.3%         |

## Asset Allocation

- Equities: 65%
  - US: 30%
  - Europe: 15%
  - Asia Pacific: 12%
  - Emerging Markets: 8%
- Bonds: 20% 
  - Government: 10%
  - Corporate: 10%
- Cash: 10%
- Others: 5%

## Top 10 Holdings

1. Apple Inc. (3.5%)
2. Microsoft Corp. (3.2%)
3. Amazon.com Inc. (2.8%)
4. Alphabet Inc. (2.5%)
5. Taiwan Semiconductor (2.0%)
""",
        "client_id": "client-4",
        "metadata": {
            "fund_name": "Global Growth Fund",
            "as_of_date": (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
            "risk_rating": "Moderate"
        }
    }
}

# Sample products
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
    },
    {
        "id": "prod-4",
        "name": "Critical Illness Protector",
        "type": "critical_illness",
        "description": "Coverage for major illnesses with lump sum payment",
        "features": [
            "Covers up to 37 critical illnesses",
            "Lump sum payment upon diagnosis",
            "No restriction on use of funds",
            "Optional return of premium"
        ],
        "min_coverage": 50000,
        "max_coverage": 500000,
        "min_age": 18,
        "max_age": 60
    },
    {
        "id": "prod-5",
        "name": "Global Investment Portfolio",
        "type": "investment",
        "description": "Investment-linked policy with global fund options",
        "features": [
            "Access to over 20 global funds",
            "Flexibility to switch funds",
            "Basic life insurance coverage",
            "Regular or single premium options"
        ],
        "min_coverage": 10000,
        "max_coverage": 1000000,
        "min_age": 18,
        "max_age": 65
    }
]

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

# Document Retrieval Tool
def document_retrieval_tool(
    query: str,
    client_id: Optional[str] = None,
    document_type: Optional[str] = None,
    limit: int = 5,
    db = None  # Dummy parameter to keep the signature compatible
) -> List[Dict[str, Any]]:
    """
    Mock document retrieval that returns documents matching the query and filters
    """
    logger.info(f"Document retrieval: query={query}, client_id={client_id}, type={document_type}")
    
    # Filter documents based on criteria
    filtered_docs = []
    for doc_id, doc in MOCK_DOCUMENTS.items():
        # Check if document matches client_id filter
        if client_id and str(doc["client_id"]) != str(client_id):
            continue
        
        # Check if document matches type filter
        if document_type and doc["type"] != document_type:
            continue
        
        # Simple keyword search in title and content
        query_lower = query.lower()
        if (query_lower in doc["title"].lower() or 
            query_lower in doc["content"].lower()):
            filtered_docs.append(doc)
    
    # Return up to the limit
    return filtered_docs[:limit]

# Client Database Tool
def client_db_tool(
    client_id: str,
    db = None  # Dummy parameter to keep the signature compatible
) -> Dict[str, Any]:
    """
    Mock client database that returns client data based on ID
    """
    logger.info(f"Client DB lookup: client_id={client_id}")
    
    # Check if client exists
    if client_id not in MOCK_CLIENTS:
        logger.error(f"Client with ID {client_id} not found")
        return {}
    
    client = MOCK_CLIENTS[client_id]
    
    # Get client's policies
    client_policies = []
    for policy_id, policy in MOCK_POLICIES.items():
        if str(policy["client_id"]) == str(client_id):
            client_policies.append(policy)
    
    # Return formatted client data
    return {
        **client,
        "policies": client_policies
    }

# Product Database Tool
def product_db_tool(
    query: str = None,
    product_type: str = None,
    db = None  # Dummy parameter to keep the signature compatible
) -> List[Dict[str, Any]]:
    """
    Mock product database that returns matching products
    """
    logger.info(f"Product DB search: query={query}, type={product_type}")
    
    # Filter products based on criteria
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
def compliance_rules_tool(
    query: str = None,
    rule_type: str = None,
    db = None  # Dummy parameter to keep the signature compatible
) -> List[Dict[str, Any]]:
    """
    Mock compliance rules that returns matching rules
    """
    logger.info(f"Compliance rules search: query={query}, type={rule_type}")
    
    # Filter rules based on criteria
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
def market_data_tool(
    fund_name: str = None,
    time_period: str = "1y",
    db = None  # Dummy parameter to keep the signature compatible
) -> Dict[str, Any]:
    """
    Mock market data that returns fund performance data
    """
    logger.info(f"Market data lookup: fund={fund_name}, period={time_period}")
    
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