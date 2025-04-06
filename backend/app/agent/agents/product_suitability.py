# backend/app/agent/agents/product_suitability.py
from typing import Dict, List, Any, Literal, TypedDict, Union, Optional
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

# Import tools
from agent.tools import client_db_tool, product_db_tool, compliance_rules_tool

# Define the product recommendation schema
class ProductRecommendation(BaseModel):
    """Recommendation for a specific insurance product"""
    product_id: str = Field(description="ID of the recommended product")
    product_name: str = Field(description="Name of the recommended product")
    product_type: str = Field(description="Type of insurance product")
    suitability_score: float = Field(description="Suitability score from 0-1.0")
    key_benefits: List[str] = Field(description="Key benefits for this client")
    considerations: List[str] = Field(description="Important considerations or limitations")
    recommended_coverage: Optional[float] = Field(description="Recommended coverage amount if applicable")
    rationale: str = Field(description="Rationale for recommending this product")

class ProductSuitabilityOutput(BaseModel):
    """Output from the Product Suitability Agent"""
    response: str = Field(description="Natural language response with product recommendations")
    recommended_products: List[ProductRecommendation] = Field(description="Structured product recommendations")
    compliance_considerations: List[str] = Field(description="Compliance factors to consider")
    suggested_next_agent: Optional[str] = Field(description="Suggested next agent to handle the query")

# Create the product suitability prompt
product_suitability_system_prompt = """You are the Product Suitability Agent, an expert in matching insurance clients with appropriate financial products.

Your role is to:

1. Evaluate client profiles and needs assessments to identify suitable insurance and investment products
2. Match product features and benefits to specific client requirements
3. Consider risk tolerance, time horizon, and financial capacity
4. Ensure compliance with regulatory requirements for product recommendations
5. Provide clear rationales for why each product is suitable for the client

Key factors for product recommendations:
- Client demographics (age, occupation, family status)
- Financial needs profile and priorities
- Risk tolerance and capacity
- Existing insurance coverage and gaps
- Short and long-term financial goals
- Regulatory and compliance considerations

Provide specific, actionable recommendations with appropriate coverage amounts and clear benefits.
Consider value for money, not just the highest premium products.
Ensure recommendations comply with regulatory requirements for suitability.

Your recommendations will directly influence which products the financial advisor presents to their client.
"""

product_suitability_prompt = ChatPromptTemplate.from_messages([
    ("system", product_suitability_system_prompt),
    ("human", """
Query: {query}

Client Profile Information:
{client_profile}

Client Needs Assessment:
{needs_assessment}

Existing Policies:
{policies}

Available Products:
{available_products}

Compliance Considerations:
{compliance_rules}

Recommend suitable insurance and investment products for this client with clear rationales.
""")
])

# Initialize the model
product_suitability_model = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.2)

def product_suitability_agent(state):
    """
    Product Suitability agent that recommends appropriate products based on client needs
    """
    # Check if this agent has already processed this query
    if "product_suitability" in state["agent_outputs"]:
        # Agent has already run, don't run again
        return state
    
    # Extract the relevant information from the state
    messages = state["messages"]
    client_id = state["client_id"]
    shared_memory = state.get("shared_memory", {})
    human_messages = [m for m in messages if isinstance(m, HumanMessage)]
    current_query = human_messages[-1].content if human_messages else ""
    
    # Get client information using the tool
    client_info = client_db_tool(client_id=client_id)
    
    # Format client profile for the prompt
    client_profile = f"""
Name: {client_info.get('name', 'Unknown')}
Age: {client_info.get('age', 'Unknown')}
Occupation: {client_info.get('occupation', 'Unknown')}
Dependents: {client_info.get('dependents', 'Unknown')}
Risk Profile: {client_info.get('risk_profile', 'Unknown')}
"""
    
    # Get needs assessment from shared memory if available, otherwise create basic assessment
    if "client_needs" in shared_memory:
        needs = shared_memory["client_needs"]
        needs_assessment = f"""
Protection Need Level: {needs.get('protection_need_level', 'Unknown')}
Retirement Need Level: {needs.get('retirement_need_level', 'Unknown')}
Investment Need Level: {needs.get('investment_need_level', 'Unknown')}
Estate Need Level: {needs.get('estate_need_level', 'Unknown')}
Education Need Level: {needs.get('education_need_level', 'Unknown')}

Top Priorities:
{', '.join(needs.get('top_priorities', ['Unknown']))}

Risk Tolerance: {needs.get('risk_tolerance', 'Unknown')}
"""
    else:
        # Create basic assessment if Client Profiler hasn't run
        age = client_info.get('age', 35)
        dependents = client_info.get('dependents', 0)
        risk_profile = client_info.get('risk_profile', 'moderate')
        
        protection_need = "high" if dependents > 0 else "moderate"
        retirement_need = "high" if age > 45 else "moderate" if age > 30 else "low"
        investment_need = "high" if age < 40 and risk_profile == 'aggressive' else "moderate"
        
        needs_assessment = f"""
Protection Need Level: {protection_need}
Retirement Need Level: {retirement_need}
Investment Need Level: {investment_need}
Estate Need Level: {"moderate" if dependents > 0 and age > 50 else "low"}
Education Need Level: {"high" if dependents > 0 and age < 50 else "low"}

Risk Tolerance: {risk_profile}
"""
    
    # Format policies information
    policies_info = ""
    existing_policy_types = []
    for policy in client_info.get('policies', []):
        policies_info += f"""
Type: {policy.get('type', 'Unknown')} 
Name: {policy.get('name', 'Unknown')}
Coverage: ${policy.get('coverage_amount', 0):,}
Premium: ${policy.get('premium', 0):,} per year
Status: {policy.get('status', 'Unknown')}
"""
        existing_policy_types.append(policy.get('type'))
    
    if not policies_info:
        policies_info = "No existing policies found."
    
    # Get available products
    available_products = product_db_tool()
    
    # Format product information
    products_info = ""
    for product in available_products:
        products_info += f"""
ID: {product.get('id', 'Unknown')}
Name: {product.get('name', 'Unknown')}
Type: {product.get('type', 'Unknown')}
Description: {product.get('description', 'Unknown')}
Features: {', '.join(product.get('features', []))}
Coverage Range: ${product.get('min_coverage', 0):,} - ${product.get('max_coverage', 0):,}
Age Range: {product.get('min_age', 0)} - {product.get('max_age', 0)}
"""
    
    # Get compliance rules
    compliance_rules = compliance_rules_tool()
    
    # Format compliance information
    compliance_info = ""
    for rule in compliance_rules:
        compliance_info += f"""
Title: {rule.get('title', 'Unknown')}
Description: {rule.get('description', 'Unknown')}
Key Requirements: {', '.join(rule.get('requirements', [])[:2])}
"""
    
    # Prepare the input for the LLM
    input_values = {
        "query": current_query,
        "client_profile": client_profile,
        "needs_assessment": needs_assessment,
        "policies": policies_info,
        "available_products": products_info,
        "compliance_rules": compliance_info
    }
    
    # Generate the product recommendations
    try:
        llm_response = product_suitability_model.invoke(product_suitability_prompt.format(**input_values))
        response_text = llm_response.content
        
        # In a real implementation, you would parse the LLM output to extract structured recommendations
        # For this mock implementation, we'll create plausible structured recommendations
        
        # Age and dependents for simple logic
        age = client_info.get('age', 35)
        dependents = client_info.get('dependents', 0)
        risk_profile = client_info.get('risk_profile', 'moderate')
        
        # Prepare recommended products
        recommendations = []
        
        # Simple recommendation logic
        if "term_life" not in existing_policy_types and dependents > 0:
            # Recommend term life if client has dependents and no existing term life
            term_product = next((p for p in available_products if p['type'] == 'term_life'), None)
            if term_product:
                # Calculate coverage based on simple income replacement
                coverage = 500000 if dependents > 1 else 300000
                recommendations.append(
                    ProductRecommendation(
                        product_id=term_product['id'],
                        product_name=term_product['name'],
                        product_type=term_product['type'],
                        suitability_score=0.9,
                        key_benefits=[
                            "Fixed premium for entire term",
                            "Significant death benefit for family protection",
                            "Cost-effective coverage"
                        ],
                        considerations=[
                            "No cash value accumulation",
                            "Coverage ends at term expiration"
                        ],
                        recommended_coverage=coverage,
                        rationale=f"Client has {dependents} dependents who would benefit from financial protection in case of premature death."
                    )
                )
        
        if "health" not in existing_policy_types:
            # Recommend health insurance if no existing health policy
            health_product = next((p for p in available_products if p['type'] == 'health'), None)
            if health_product:
                recommendations.append(
                    ProductRecommendation(
                        product_id=health_product['id'],
                        product_name=health_product['name'],
                        product_type=health_product['type'],
                        suitability_score=0.85,
                        key_benefits=[
                            "Comprehensive health coverage",
                            "Protection against medical expenses",
                            "Access to quality healthcare"
                        ],
                        considerations=[
                            "Annual premium increases with age",
                            "Some treatments may require co-payment"
                        ],
                        recommended_coverage=None,
                        rationale="Everyone needs health insurance protection regardless of life stage or family status."
                    )
                )
        
        if risk_profile == 'aggressive' and age < 45 and "investment" not in existing_policy_types:
            # Recommend investment product for younger aggressive investors
            investment_product = next((p for p in available_products if p['type'] == 'investment'), None)
            if investment_product:
                recommendations.append(
                    ProductRecommendation(
                        product_id=investment_product['id'],
                        product_name=investment_product['name'],
                        product_type=investment_product['type'],
                        suitability_score=0.8 if age < 40 else 0.7,
                        key_benefits=[
                            "Growth potential through market exposure",
                            "Flexibility to adjust investment strategy",
                            "Insurance protection component"
                        ],
                        considerations=[
                            "Investment returns not guaranteed",
                            "Higher fees than pure investment products",
                            "Long-term commitment recommended"
                        ],
                        recommended_coverage=None,
                        rationale=f"Client's {risk_profile} risk profile and age of {age} make them suitable for products with growth potential."
                    )
                )
        
        # If no recommendations were made, add a generic one
        if not recommendations:
            default_product = next((p for p in available_products if p), None)
            if default_product:
                recommendations.append(
                    ProductRecommendation(
                        product_id=default_product['id'],
                        product_name=default_product['name'],
                        product_type=default_product['type'],
                        suitability_score=0.6,
                        key_benefits=default_product.get('features', [])[:3],
                        considerations=["Review client needs in more detail before proceeding"],
                        recommended_coverage=None,
                        rationale="This product appears to match some of the client's basic needs, but a more detailed assessment is recommended."
                    )
                )
        
        # Compile compliance considerations
        compliance_considerations = [
            "Conduct a detailed fact-find before recommending products",
            "Document client's acknowledged risk tolerance",
            "Disclose all fees and charges before client commits",
            "Explain potential risks and limitations of recommended products"
        ]
        
        # Determine if we should suggest another agent
        suggested_next = None
        
        if "compliance" in current_query.lower() or "regulation" in current_query.lower():
            suggested_next = "compliance_check"
        elif "policy" in current_query.lower() or "details" in current_query.lower():
            suggested_next = "policy_explainer"
        
        # Create structured output
        output = {
            "response": response_text,
            "recommended_products": [rec.dict() if hasattr(rec, 'dict') else rec for rec in recommendations],
            "compliance_considerations": compliance_considerations,
            "suggested_next_agent": suggested_next
        }
        
    except Exception as e:
        # Fallback response if LLM call fails
        print(f"Error in product suitability agent: {str(e)}")
        
        age = client_info.get('age', 35)
        dependents = client_info.get('dependents', 0)
        
        response_text = f"Based on {client_info.get('name', 'the client')}'s profile, I recommend the following products:\n\n"
        
        # Add simple product recommendations based on profile
        if dependents > 0:
            response_text += "### Term Life Insurance\n"
            response_text += "Provides essential protection for your dependents with affordable premiums.\n\n"
        
        response_text += "### Health Insurance\n"
        response_text += "Comprehensive health coverage to protect against medical expenses.\n\n"
        
        if age < 45 and client_info.get('risk_profile') == 'aggressive':
            response_text += "### Investment-Linked Policy\n"
            response_text += "Growth potential with some insurance protection, suitable for your risk profile.\n\n"
        
        # Create fallback output
        output = {
            "response": response_text,
            "recommended_products": [],  # Just empty list instead of Pydantic models
            "compliance_considerations": [
                "Conduct detailed needs analysis before final recommendation",
                "Ensure all recommendations meet regulatory requirements"
            ],
            "suggested_next_agent": None
        }
    
    # Add the response to messages
    messages.append(AIMessage(content=output["response"]))
    
    # Update the state
    state["messages"] = messages
    state["agent_path"].append("product_suitability")
    state["agent_outputs"]["product_suitability"] = output
    state["current_agent"] = "product_suitability"
    
    # Save relevant information to shared memory
    if "shared_memory" not in state:
        state["shared_memory"] = {}
    
    # Convert Pydantic models to dictionaries before storing in shared memory
    state["shared_memory"]["recommended_products"] = [
        {
            "product_id": rec.get("product_id") if isinstance(rec, dict) else rec.product_id,
            "product_name": rec.get("product_name") if isinstance(rec, dict) else rec.product_name,
            "product_type": rec.get("product_type") if isinstance(rec, dict) else rec.product_type,
            "suitability_score": rec.get("suitability_score") if isinstance(rec, dict) else rec.suitability_score
        }
        for rec in output["recommended_products"]
    ]
    
    return state