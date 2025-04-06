# backend/app/agent/agents/review_upsell.py
from typing import Dict, List, Any, Literal, TypedDict, Union, Optional
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from datetime import datetime

# Import tools
from agent.tools import client_db_tool, product_db_tool

# Define opportunity schema
class ReviewOpportunity(BaseModel):
    """Opportunity for policy review"""
    policy_id: str = Field(description="ID of the policy to review")
    policy_name: str = Field(description="Name of the policy")
    policy_type: str = Field(description="Type of policy")
    review_reason: str = Field(description="Reason for recommending review")
    review_priority: Literal["high", "medium", "low"] = Field(description="Priority of the review")
    due_date: Optional[str] = Field(description="When the review should be conducted")

class UpsellOpportunity(BaseModel):
    """Opportunity for additional product sales"""
    product_id: str = Field(description="ID of the recommended product")
    product_name: str = Field(description="Name of the recommended product")
    product_type: str = Field(description="Type of product")
    opportunity_reason: str = Field(description="Reason for the upsell opportunity")
    potential_value: Literal["high", "medium", "low"] = Field(description="Potential value of the opportunity")
    coverage_gap: str = Field(description="Coverage gap being addressed")

class ReviewUpsellOutput(BaseModel):
    """Output from the Review & Upsell Agent"""
    response: str = Field(description="Natural language response outlining opportunities")
    review_opportunities: List[ReviewOpportunity] = Field(description="Structured review opportunities")
    upsell_opportunities: List[UpsellOpportunity] = Field(description="Structured upsell opportunities")
    next_steps: List[str] = Field(description="Recommended next steps for the advisor")
    suggested_next_agent: Optional[str] = Field(description="Suggested next agent to handle the query")

# Create the review & upsell prompt
review_upsell_system_prompt = """You are the Review & Upsell Agent, an expert in identifying policy review needs and sales opportunities.

Your role is to:

1. Identify policies that need review due to life events, expiry, or changes in client circumstances
2. Detect coverage gaps in the client's insurance portfolio
3. Recognize potential upsell opportunities based on client profile and needs
4. Prioritize review and upsell opportunities by importance and value
5. Suggest practical next steps for financial advisors to pursue these opportunities

Key factors to consider:
- Upcoming policy renewals or expiry dates
- Changes in client's life circumstances (age, dependents, career)
- Coverage gaps compared to typical needs for similar profiles
- Policy performance and market changes
- Scheduled review dates and regulatory requirements

Be strategic in identifying high-value opportunities.
Focus on genuine client needs rather than just maximizing sales.
Provide clear, actionable next steps for the financial advisor.

Your insights will help financial advisors maintain client relationships and ensure ongoing coverage adequacy.
"""

review_upsell_prompt = ChatPromptTemplate.from_messages([
    ("system", review_upsell_system_prompt),
    ("human", """
Query: {query}

Client Profile:
{client_profile}

Current Policies:
{current_policies}

Available Products:
{available_products}

Client Needs Assessment:
{needs_assessment}

Please identify review needs and upsell opportunities for this client.
""")
])

# Initialize the model
review_upsell_model = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.2)

def review_upsell_agent(state):
    """
    Review & Upsell agent that identifies policy review needs and sales opportunities
    """
    # Check if this agent has already processed this query
    if "review_upsell" in state["agent_outputs"]:
        # Agent has already run, don't run again
        return state
    
    # Extract the relevant information from the state
    messages = state["messages"]
    client_id = state["client_id"]
    shared_memory = state.get("shared_memory", {})
    human_messages = [m for m in messages if isinstance(m, HumanMessage)]
    current_query = human_messages[-1].content if human_messages else ""
    
    # Get client information
    client_info = client_db_tool(client_id=client_id)
    
    # Format client profile
    client_profile = f"""
Name: {client_info.get('name', 'Unknown')}
Age: {client_info.get('age', 'Unknown')}
Occupation: {client_info.get('occupation', 'Unknown')}
Dependents: {client_info.get('dependents', 'Unknown')}
Risk Profile: {client_info.get('risk_profile', 'Unknown')}
Category: {client_info.get('category', 'Unknown')}
Next Review Date: {client_info.get('next_review_date', 'Not scheduled')}
"""
    
    # Format current policies
    current_policies = ""
    existing_policy_types = []
    
    for policy in client_info.get('policies', []):
        current_policies += f"""
ID: {policy.get('id', 'Unknown')}
Type: {policy.get('type', 'Unknown')} 
Name: {policy.get('name', 'Unknown')}
Coverage: ${policy.get('coverage_amount', 0):,}
Premium: ${policy.get('premium', 0):,} per year
Status: {policy.get('status', 'Unknown')}
Start Date: {policy.get('start_date', 'Unknown')}
End Date: {policy.get('end_date', 'N/A')}
"""
        existing_policy_types.append(policy.get('type'))
    
    if not current_policies:
        current_policies = "No existing policies found."
    
    # Get available products
    available_products = product_db_tool()
    
    # Format available products info
    products_info = ""
    for product in available_products:
        products_info += f"""
ID: {product.get('id', 'Unknown')}
Name: {product.get('name', 'Unknown')}
Type: {product.get('type', 'Unknown')}
Description: {product.get('description', 'Unknown')}
Features: {', '.join(product.get('features', []))}
"""
    
    # Get needs assessment from shared memory if available
    needs_assessment = ""
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
        
        needs_assessment = f"""
Protection Need Level: {"high" if dependents > 0 else "moderate"}
Retirement Need Level: {"high" if age > 45 else "moderate" if age > 30 else "low"}
Investment Need Level: {"high" if age < 40 and risk_profile == 'aggressive' else "moderate"}
Estate Need Level: {"moderate" if dependents > 0 and age > 50 else "low"}
Education Need Level: {"high" if dependents > 0 and age < 50 else "low"}

Risk Tolerance: {risk_profile}
"""
    
    # Prepare the input for the LLM
    input_values = {
        "query": current_query,
        "client_profile": client_profile,
        "current_policies": current_policies,
        "available_products": products_info,
        "needs_assessment": needs_assessment
    }
    
    # Generate the review and upsell opportunities
    try:
        llm_response = review_upsell_model.invoke(review_upsell_prompt.format(**input_values))
        response_text = llm_response.content
        
        # In a real implementation, you would parse the LLM output to extract structured data
        # For this mock implementation, we'll create plausible structured data
        
        # Basic client info for logic
        age = client_info.get('age', 35)
        dependents = client_info.get('dependents', 0)
        policies = client_info.get('policies', [])
        
        # Identify review opportunities
        review_opportunities = []
        
        # Look for policies approaching renewal or review
        for policy in policies:
            # Check if policy has an end date and it's within a year
            if policy.get('end_date'):
                try:
                    end_date = datetime.strptime(policy.get('end_date'), "%Y-%m-%d")
                    today = datetime.now()
                    days_until_expiry = (end_date - today).days
                    
                    if 0 < days_until_expiry < 180:  # Within 6 months
                        review_opportunities.append(
                            ReviewOpportunity(
                                policy_id=policy.get('id', 'Unknown'),
                                policy_name=policy.get('name', 'Unknown'),
                                policy_type=policy.get('type', 'Unknown'),
                                review_reason=f"Policy expiring in {days_until_expiry} days",
                                review_priority="high" if days_until_expiry < 90 else "medium",
                                due_date=(today + timedelta(days=min(30, days_until_expiry // 2))).strftime("%Y-%m-%d")
                            )
                        )
                except:
                    # If date parsing fails, add a generic review opportunity
                    if policy.get('type') == "term_life" or policy.get('type') == "health":
                        review_opportunities.append(
                            ReviewOpportunity(
                                policy_id=policy.get('id', 'Unknown'),
                                policy_name=policy.get('name', 'Unknown'),
                                policy_type=policy.get('type', 'Unknown'),
                                review_reason="Annual policy review recommended",
                                review_priority="medium",
                                due_date=None
                            )
                        )
        
        # If no specific review opportunities, add general reviews based on client profile
        if not review_opportunities and policies:
            # Add a general review opportunity for the first policy
            policy = policies[0]
            review_opportunities.append(
                ReviewOpportunity(
                    policy_id=policy.get('id', 'Unknown'),
                    policy_name=policy.get('name', 'Unknown'),
                    policy_type=policy.get('type', 'Unknown'),
                    review_reason="Regular policy review to ensure coverage remains appropriate",
                    review_priority="medium",
                    due_date=None
                )
            )
        
        # Identify upsell opportunities
        upsell_opportunities = []
        policy_types = [p.get('type') for p in policies]
        
        # Check for missing policy types
        if 'critical_illness' not in policy_types:
            # Find critical illness product
            ci_product = next((p for p in available_products if p['type'] == 'critical_illness'), None)
            if ci_product:
                upsell_opportunities.append(
                    UpsellOpportunity(
                        product_id=ci_product['id'],
                        product_name=ci_product['name'],
                        product_type=ci_product['type'],
                        opportunity_reason="No critical illness coverage in current portfolio",
                        potential_value="high" if age > 40 else "medium",
                        coverage_gap="Protection against major illnesses and associated financial impact"
                    )
                )
        
        if 'investment' not in policy_types and age < 50 and client_info.get('risk_profile') != 'conservative':
            # Find investment product
            inv_product = next((p for p in available_products if p['type'] == 'investment'), None)
            if inv_product:
                upsell_opportunities.append(
                    UpsellOpportunity(
                        product_id=inv_product['id'],
                        product_name=inv_product['name'],
                        product_type=inv_product['type'],
                        opportunity_reason=f"Client's {client_info.get('risk_profile', 'moderate')} risk profile suitable for growth products",
                        potential_value="high" if age < 40 else "medium",
                        coverage_gap="Long-term wealth accumulation and growth potential"
                    )
                )
        
        if dependents > 0 and 'term_life' not in policy_types and 'whole_life' not in policy_types:
            # Find life insurance product
            life_product = next((p for p in available_products if p['type'] == 'term_life' or p['type'] == 'whole_life'), None)
            if life_product:
                upsell_opportunities.append(
                    UpsellOpportunity(
                        product_id=life_product['id'],
                        product_name=life_product['name'],
                        product_type=life_product['type'],
                        opportunity_reason=f"Client has {dependents} dependents without life insurance protection",
                        potential_value="high",
                        coverage_gap="Family financial protection in case of premature death"
                    )
                )
        
        # Next steps
        next_steps = [
            "Schedule a portfolio review meeting with the client",
            "Prepare personalized illustrations for recommended products",
            "Develop a coverage enhancement proposal addressing key gaps"
        ]
        
        if review_opportunities:
            next_steps.insert(0, f"Contact client about upcoming review for {review_opportunities[0].policy_name}")
        
        # Determine if we should suggest another agent
        suggested_next = None
        
        if "product" in current_query.lower() or "recommend" in current_query.lower():
            suggested_next = "product_suitability"
        elif "compliance" in current_query.lower():
            suggested_next = "compliance_check"
        
        # Create structured output
        output = {
            "response": response_text,
            "review_opportunities": [opp.dict() for opp in review_opportunities],
            "upsell_opportunities": [opp.dict() for opp in upsell_opportunities],
            "next_steps": next_steps,
            "suggested_next_agent": suggested_next
        }
        
    except Exception as e:
        # Fallback response if LLM call fails
        print(f"Error in review & upsell agent: {str(e)}")
        
        response_text = f"## Review & Upsell Opportunities for {client_info.get('name', 'the client')}\n\n"
        
        # Check for review opportunities based on next_review_date
        if client_info.get('next_review_date'):
            response_text += f"The client's next review is scheduled for {client_info.get('next_review_date')}.\n\n"
        
        # Add upsell opportunities based on client profile
        response_text += "### Potential Opportunities:\n\n"
        
        age = client_info.get('age', 35)
        dependents = client_info.get('dependents', 0)
        policies = client_info.get('policies', [])
        policy_types = [p.get('type') for p in policies]
        
        if 'critical_illness' not in policy_types:
            response_text += "1. **Critical Illness Coverage**: The client does not have critical illness protection. "
            response_text += "This would provide a lump sum payment upon diagnosis of a covered serious illness.\n\n"
        
        if 'investment' not in policy_types and age < 50:
            response_text += "2. **Investment-Linked Policy**: Given the client's age, an ILP could provide growth potential "
            response_text += "while maintaining some insurance coverage.\n\n"
        
        if dependents > 0 and 'term_life' not in policy_types and 'whole_life' not in policy_types:
            response_text += "3. **Life Insurance**: With dependents to protect, the client should consider life insurance "
            response_text += "to provide financial security for their family.\n\n"
        
        response_text += "\nRecommended next steps:\n"
        response_text += "1. Schedule a review meeting to discuss these opportunities\n"
        response_text += "2. Prepare personalized illustrations for the recommended products\n"
        response_text += "3. Focus on how these additions would complement their existing portfolio\n"
        
        # Create fallback output with minimal structure
        output = {
            "response": response_text,
            "review_opportunities": [],
            "upsell_opportunities": [],
            "next_steps": [
                "Schedule a review meeting",
                "Prepare product illustrations",
                "Develop a coverage enhancement proposal"
            ],
            "suggested_next_agent": None
        }
    
    # Add the response to messages
    messages.append(AIMessage(content=output["response"]))
    
    # Update the state
    state["messages"] = messages
    state["agent_path"].append("review_upsell")
    state["agent_outputs"]["review_upsell"] = output
    state["current_agent"] = "review_upsell"
    
    # Save relevant information to shared memory
    if "shared_memory" not in state:
        state["shared_memory"] = {}
    
    # Handle both Pydantic model and dictionary formats for upsell opportunities
    upsell_opps = output["upsell_opportunities"]
    shared_upsell = []
    
    for opp in upsell_opps:
        if hasattr(opp, 'dict'):
            # It's a Pydantic model
            shared_upsell.append({
                "product_type": opp.product_type,
                "product_name": opp.product_name,
                "potential_value": opp.potential_value
            })
        else:
            # It's already a dictionary
            shared_upsell.append({
                "product_type": opp.get("product_type", "Unknown"),
                "product_name": opp.get("product_name", "Unknown"),
                "potential_value": opp.get("potential_value", "medium")
            })
    
    state["shared_memory"]["upsell_opportunities"] = shared_upsell
    
    return state