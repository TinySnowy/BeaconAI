# backend/app/agent/agents/compliance_check.py
from typing import Dict, List, Any, Literal, TypedDict, Union, Optional
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

# Import tools
from agent.tools import compliance_rules_tool, client_db_tool, document_retrieval_tool

# Define compliance assessment schema
class ComplianceRequirement(BaseModel):
    """Individual compliance requirement assessment"""
    requirement: str = Field(description="The specific compliance requirement")
    rule_source: str = Field(description="Source of the compliance rule")
    status: Literal["compliant", "non-compliant", "attention-needed", "not-applicable"] = Field(description="Compliance status")
    explanation: str = Field(description="Explanation of the compliance status")
    action_needed: Optional[str] = Field(description="Action needed to ensure compliance, if any")

class ComplianceCheckOutput(BaseModel):
    """Output from the Compliance Check Agent"""
    response: str = Field(description="Natural language explanation of compliance considerations")
    compliance_requirements: List[ComplianceRequirement] = Field(description="Assessment of specific compliance requirements")
    key_compliance_issues: List[str] = Field(description="Key compliance issues to address")
    document_references: List[Dict[str, str]] = Field(description="References to compliance documents")
    suggested_next_agent: Optional[str] = Field(description="Suggested next agent to handle the query")

# Create the compliance check prompt
compliance_check_system_prompt = """You are the Compliance Check Agent, an expert in financial advisory regulations and compliance requirements.

Your role is to:

1. Apply relevant regulatory requirements to financial advice scenarios
2. Identify potential compliance issues in advisor-client interactions
3. Provide clear guidance on regulatory obligations
4. Ensure recommendations meet suitability and disclosure requirements
5. Help advisors maintain proper documentation for compliance purposes

Key compliance areas to consider:
- Know Your Customer (KYC) requirements
- Needs-based selling requirements
- Full and proper disclosure obligations
- Suitability of recommendations
- Documentation and record-keeping requirements
- Conflicting interests management

Be precise about regulatory requirements while making them practical to implement.
Prioritize client protection and transparency.
Focus on compliance requirements for insurance and investment products.

Your guidance will help financial advisors ensure their recommendations are compliant with regulatory requirements.
"""

compliance_check_prompt = ChatPromptTemplate.from_messages([
    ("system", compliance_check_system_prompt),
    ("human", """
Query: {query}

Client Profile:
{client_profile}

Product Recommendations:
{product_recommendations}

Relevant Compliance Rules:
{compliance_rules}

Please analyze the compliance implications and requirements in this context.
""")
])

# Initialize the model
compliance_check_model = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.1)

def compliance_check_agent(state):
    """
    Compliance Check agent that assesses regulatory compliance
    """
    # Check if this agent has already processed this query
    if "compliance_check" in state["agent_outputs"]:
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
"""
    
    # Get product recommendations from shared memory
    product_recommendations = ""
    if "recommended_products" in shared_memory:
        recommendations = shared_memory["recommended_products"]
        for rec in recommendations:
            product_recommendations += f"""
Product: {rec.get('product_name', 'Unknown')}
Type: {rec.get('product_type', 'Unknown')}
Suitability Score: {rec.get('suitability_score', 'Unknown')}
"""
    else:
        # If no recommendations in shared memory, create placeholder
        product_recommendations = "No specific product recommendations available for compliance review."
    
    # Get compliance rules
    rules = compliance_rules_tool()
    
    # Format compliance rules
    compliance_rules = ""
    document_references = []
    
    for rule in rules:
        compliance_rules += f"""
Title: {rule.get('title', 'Unknown')}
Type: {rule.get('type', 'Unknown')}
Description: {rule.get('description', 'Unknown')}
Requirements:
"""
        for req in rule.get('requirements', []):
            compliance_rules += f"- {req}\n"
        
        document_references.append({
            "id": rule.get("id", "rule-id"),
            "title": rule.get("title", "Compliance Rule"),
            "type": "regulatory",
            "snippet": rule.get("description", "")
        })
    
    # Retrieve any regulatory documents
    regulatory_docs = document_retrieval_tool(
        query=current_query,
        client_id=None,  # Regulatory docs aren't client-specific
        document_type="regulatory"
    )
    
    for doc in regulatory_docs:
        if doc.get("id") not in [ref.get("id") for ref in document_references]:
            document_references.append({
                "id": doc.get("id", "doc-id"),
                "title": doc.get("title", "Regulatory Document"),
                "type": "regulatory",
                "snippet": doc.get("content", "")[:150] + "..."
            })
    
    # Prepare the input for the LLM
    input_values = {
        "query": current_query,
        "client_profile": client_profile,
        "product_recommendations": product_recommendations,
        "compliance_rules": compliance_rules
    }
    
    # Generate the compliance assessment
    try:
        llm_response = compliance_check_model.invoke(compliance_check_prompt.format(**input_values))
        response_text = llm_response.content
        
        # In a real implementation, you would parse the LLM output to extract structured assessment
        # For this mock implementation, we'll create plausible structured assessment
        
        # Identify common compliance requirements based on available rules
        requirements = []
        
        # KYC requirement
        requirements.append(
            ComplianceRequirement(
                requirement="Know Your Client (KYC) documentation",
                rule_source="MAS Notice FAA-N16",
                status="attention-needed",
                explanation="Ensure comprehensive client information is documented, including financial situation, investment experience, and risk tolerance.",
                action_needed="Complete and document full KYC process before recommending products."
            )
        )
        
        # Suitability assessment
        requirements.append(
            ComplianceRequirement(
                requirement="Product Suitability Assessment",
                rule_source="MAS Notice FAA-N16",
                status="compliant" if "recommended_products" in shared_memory else "attention-needed",
                explanation="Products must match client's risk profile, financial objectives, and needs.",
                action_needed=None if "recommended_products" in shared_memory else "Conduct and document suitability assessment for each product recommendation."
            )
        )
        
        # Disclosure requirement
        requirements.append(
            ComplianceRequirement(
                requirement="Fee and Risk Disclosure",
                rule_source="FAIR Principles",
                status="attention-needed",
                explanation="All fees, charges, and product risks must be clearly disclosed to the client.",
                action_needed="Prepare disclosure documents highlighting all fees and risks for recommended products."
            )
        )
        
        # Documentation
        requirements.append(
            ComplianceRequirement(
                requirement="Advice Documentation",
                rule_source="Internal Policy",
                status="attention-needed",
                explanation="All advice and recommendations must be properly documented with rationale.",
                action_needed="Document reasoning for recommendations in client file."
            )
        )
        
        # Add ILP-specific requirement if relevant
        if "recommended_products" in shared_memory and any(p.get('product_type') == 'investment' for p in shared_memory["recommended_products"]):
            requirements.append(
                ComplianceRequirement(
                    requirement="Investment-Linked Policy Disclosure",
                    rule_source="Investment-Linked Policy Disclosure",
                    status="attention-needed",
                    explanation="Client must be informed that ILP returns are not guaranteed and understand the associated risks.",
                    action_needed="Provide and explain the Investment-Linked Product disclosure statement to client."
                )
            )
        
        # Identify key compliance issues
        key_issues = [
            "Ensure KYC process is thoroughly completed and documented",
            "Document client's acknowledgment of product risks",
            "Maintain records of advice process and suitability assessment"
        ]
        
        # Determine if we should suggest another agent
        suggested_next = None
        
        if "product" in current_query.lower() or "recommend" in current_query.lower():
            suggested_next = "product_suitability"
        elif "policy" in current_query.lower() or "details" in current_query.lower():
            suggested_next = "policy_explainer"
        
        # Create structured output
        output = {
            "response": response_text,
            "compliance_requirements": [req.dict() for req in requirements],
            "key_compliance_issues": key_issues,
            "document_references": document_references,
            "suggested_next_agent": suggested_next
        }
        
    except Exception as e:
        # Fallback response if LLM call fails
        print(f"Error in compliance check agent: {str(e)}")
        
        response_text = "After reviewing the relevant compliance requirements:\n\n"
        
        # Add basic compliance information
        for rule in rules[:2]:
            response_text += f"### {rule.get('title', 'Compliance Rule')}\n"
            response_text += f"{rule.get('description', '')}\n\n"
            response_text += "Key requirements:\n"
            for req in rule.get('requirements', [])[:3]:
                response_text += f"- {req}\n"
            response_text += "\n"
        
        response_text += "\nBased on these regulations, ensure you:\n"
        response_text += "1. Document the client's risk profile and needs assessment\n"
        response_text += "2. Clearly disclose all product fees and risks\n"
        response_text += "3. Maintain records of the advice process\n"
        
        # Create fallback output
        simple_requirements = [
            ComplianceRequirement(
                requirement="Documentation",
                rule_source="Regulatory Guidelines",
                status="attention-needed",
                explanation="All client interactions must be documented",
                action_needed="Ensure proper documentation of advice process"
            ),
            ComplianceRequirement(
                requirement="Disclosure",
                rule_source="Regulatory Guidelines",
                status="attention-needed",
                explanation="Product risks and fees must be disclosed",
                action_needed="Provide comprehensive disclosure documents"
            )
        ]
        
        output = {
            "response": response_text,
            "compliance_requirements": simple_requirements,
            "key_compliance_issues": ["Documentation", "Disclosure", "Suitability assessment"],
            "document_references": document_references,
            "suggested_next_agent": None
        }
    
    # Add the response to messages
    messages.append(AIMessage(content=output["response"]))
    
    # Update the state
    state["messages"] = messages
    state["agent_path"].append("compliance_check")
    state["agent_outputs"]["compliance_check"] = output
    state["current_agent"] = "compliance_check"
    
    # Save relevant information to shared memory
    if "shared_memory" not in state:
        state["shared_memory"] = {}
    
    state["shared_memory"]["compliance_issues"] = output["key_compliance_issues"]
    
    return state