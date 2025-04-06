# backend/app/agent/agents/client_profiler.py
from typing import Dict, List, Any, Literal, TypedDict, Union, Optional
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

# Import tools
from agent.tools import client_db_tool, document_retrieval_tool

# Define the client profiler output schema
class ClientNeedsAssessment(BaseModel):
    """Assessment of client financial needs and priorities"""
    protection_need_level: Literal["low", "moderate", "high"] = Field(description="Level of insurance protection needed")
    retirement_need_level: Literal["low", "moderate", "high"] = Field(description="Level of retirement planning needed")
    investment_need_level: Literal["low", "moderate", "high"] = Field(description="Level of investment planning needed")
    estate_need_level: Literal["low", "moderate", "high"] = Field(description="Level of estate planning needed")
    education_need_level: Literal["low", "moderate", "high"] = Field(description="Level of education funding needed")
    top_priorities: List[str] = Field(description="Top 2-3 financial priorities based on client profile")
    risk_tolerance: Literal["conservative", "moderate", "aggressive"] = Field(description="Client's risk tolerance assessment")
    reasoning: str = Field(description="Chain-of-thought reasoning for this assessment")

class ClientProfilerOutput(BaseModel):
    """Output from the Client Profiler Agent"""
    response: str = Field(description="Natural language response explaining client needs assessment")
    needs_assessment: ClientNeedsAssessment = Field(description="Structured assessment of client needs")
    document_references: Optional[List[Dict[str, str]]] = Field(description="References to relevant documents")
    suggested_next_agent: Optional[str] = Field(description="Suggested next agent to handle the query")

# Create the client profiler prompt
client_profiler_system_prompt = """You are the Client Profiler Agent, an expert in analyzing insurance clients' financial profiles and needs. 

Your role is to:

1. Analyze the client's profile (age, occupation, dependents, risk profile, existing policies)
2. Identify their financial needs, gaps, and priorities
3. Assess their life stage and corresponding financial requirements
4. Evaluate their risk tolerance and capacity
5. Provide a clear needs assessment with actionable insights for their financial advisor

Key factors to consider:
- Life stage (starting career, family formation, pre-retirement, retirement)
- Family status (single, married, with/without children)
- Income profile and stability
- Existing insurance coverage and gaps
- Short and long-term financial goals
- Risk tolerance and capacity

Be specific in your assessment. Consider cultural and demographic factors when relevant. 
Focus on financial planning best practices and prioritize client financial security.

Your assessment will guide the financial advisor in recommending suitable insurance and investment products.
"""

client_profiler_prompt = ChatPromptTemplate.from_messages([
    ("system", client_profiler_system_prompt),
    ("human", """
Query: {query}

Client Profile Information:
{client_profile}

Existing Policies:
{policies}

Additional Documents:
{documents}

Analyze this client's financial needs, priorities, and risk profile, then provide a comprehensive needs assessment.
""")
])

# Initialize the model
client_profiler_model = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.1)

def client_profiler_agent(state):
    """
    Client Profiler agent that analyzes client needs and financial gaps
    """
    # Check if this agent has already processed this query
    if "client_profiler" in state["agent_outputs"]:
        # Agent has already run, don't run again
        return state
    
    # Extract the relevant information from the state
    messages = state["messages"]
    client_id = state["client_id"]
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
Category: {client_info.get('category', 'Unknown')}
Next Review Date: {client_info.get('next_review_date', 'Not scheduled')}
"""
    
    # Format policies information
    policies_info = ""
    for policy in client_info.get('policies', []):
        policies_info += f"""
Type: {policy.get('type', 'Unknown')} 
Name: {policy.get('name', 'Unknown')}
Coverage: ${policy.get('coverage_amount', 0):,}
Premium: ${policy.get('premium', 0):,} per year
Status: {policy.get('status', 'Unknown')}
"""
    
    if not policies_info:
        policies_info = "No existing policies found."
    
    # Retrieve relevant financial documents
    documents = document_retrieval_tool(
        query=current_query,
        client_id=client_id,
        document_type="financial"
    )
    
    # Format documents information
    documents_info = ""
    document_references = []
    for doc in documents:
        documents_info += f"\nTitle: {doc.get('title', 'Unknown')}\n"
        documents_info += f"Type: {doc.get('type', 'Unknown')}\n"
        documents_info += f"Excerpt: {doc.get('content', '')[:200]}...\n"
        
        document_references.append({
            "id": doc.get("id", "doc-id"),
            "title": doc.get("title", "Document"),
            "type": doc.get("type", "financial"),
            "snippet": doc.get("content", "")[:100] + "..."
        })
    
    if not documents_info:
        documents_info = "No relevant financial documents found."
    
    # Prepare the input for the LLM
    input_values = {
        "query": current_query,
        "client_profile": client_profile,
        "policies": policies_info,
        "documents": documents_info
    }
    
    # Generate the needs assessment
    try:
        llm_response = client_profiler_model.invoke(client_profiler_prompt.format(**input_values))
        response_text = llm_response.content
        
        # In a real implementation, you would parse the LLM output to extract structured data
        # For this mock implementation, we'll create a plausible structured assessment
        
        # Age-based defaults
        age = client_info.get('age', 35)
        dependents = client_info.get('dependents', 0)
        
        # Create structured assessment
        needs_assessment = {
            "protection_need_level": "high" if dependents > 0 else "moderate" if age < 50 else "low",
            "retirement_need_level": "high" if age > 45 else "moderate" if age > 30 else "low",
            "investment_need_level": "high" if age < 40 and client_info.get('risk_profile') == 'aggressive' else "moderate",
            "estate_need_level": "high" if dependents > 0 and age > 50 else "low",
            "education_need_level": "high" if dependents > 0 and age < 50 else "low",
            "top_priorities": [],
            "risk_tolerance": client_info.get('risk_profile', 'moderate'),
            "reasoning": f"Assessment based on client age ({age}), dependent status ({dependents}), and stated risk profile ({client_info.get('risk_profile', 'moderate')})."
        }
        
        # Determine top priorities based on profile
        priorities = []
        if dependents > 0:
            priorities.append("Family protection through adequate life insurance")
        
        if age > 45:
            priorities.append("Retirement planning and income security")
        elif age < 40:
            priorities.append("Long-term wealth accumulation")
        
        if dependents > 0 and age < 50:
            priorities.append("Education funding for dependents")
            
        if not priorities:
            priorities.append("Building emergency funds and financial security")
            
        needs_assessment["top_priorities"] = priorities[:3]  # Take top 3 at most
        
        # Determine if we should suggest another agent
        suggested_next = None
        
        if "products" in current_query.lower() or "recommend" in current_query.lower():
            suggested_next = "product_suitability"
        elif "policy" in current_query.lower() or "coverage" in current_query.lower():
            suggested_next = "policy_explainer"
        
        # Create structured output
        output = {
            "response": response_text,
            "needs_assessment": needs_assessment.dict() if isinstance(needs_assessment, BaseModel) else needs_assessment,
            "document_references": document_references if document_references else None,
            "suggested_next_agent": suggested_next
        }
        
    except Exception as e:
        # Fallback response if LLM call fails
        print(f"Error in client profiler agent: {str(e)}")
        
        response_text = f"Based on my analysis of {client_info.get('name', 'the client')}'s profile:\n\n"
        response_text += f"- Age: {client_info.get('age', 'N/A')} years old\n"
        response_text += f"- Occupation: {client_info.get('occupation', 'N/A')}\n"
        response_text += f"- Dependents: {client_info.get('dependents', 'N/A')}\n"
        response_text += f"- Risk profile: {client_info.get('risk_profile', 'N/A')}\n\n"
        
        if client_info.get('dependents', 0) > 0:
            response_text += "I recommend focusing on adequate protection for dependents through life insurance. "
        
        if client_info.get('age', 0) < 40:
            response_text += "Given the client's age, a long-term investment approach would be suitable. "
        else:
            response_text += "The client should balance growth with security as they approach retirement. "
        
        # Create fallback output
        output = {
            "response": response_text,
            "needs_assessment": {
                "protection_need_level": "moderate",
                "retirement_need_level": "moderate",
                "investment_need_level": "moderate",
                "estate_need_level": "low",
                "education_need_level": "low",
                "top_priorities": ["Financial security"],
                "risk_tolerance": client_info.get('risk_profile', 'moderate'),
                "reasoning": "Basic assessment based on client demographics."
            },
            "document_references": None,
            "suggested_next_agent": None
        }
    
    # Add the response to messages
    messages.append(AIMessage(content=output["response"]))
    
    # Update the state
    state["messages"] = messages
    state["agent_path"].append("client_profiler")
    state["agent_outputs"]["client_profiler"] = output
    state["current_agent"] = "client_profiler"
    
    # Save relevant information to shared memory
    if "shared_memory" not in state:
        state["shared_memory"] = {}
    
    state["shared_memory"]["client_needs"] = output["needs_assessment"]
    
    return state