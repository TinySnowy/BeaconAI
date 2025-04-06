# backend/app/agent/agents/policy_explainer.py
from typing import Dict, List, Any, Literal, TypedDict, Union, Optional
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

# Import tools
from agent.tools import document_retrieval_tool, client_db_tool

# Define the policy detail schema
class PolicyDetail(BaseModel):
    """Extracted details about an insurance policy"""
    policy_type: str = Field(description="Type of insurance policy")
    policy_name: str = Field(description="Name of the policy")
    coverage_amount: Optional[str] = Field(description="Coverage amount if applicable")
    premium: Optional[str] = Field(description="Premium amount if applicable")
    key_benefits: List[str] = Field(description="Key benefits of the policy")
    exclusions: List[str] = Field(description="Key exclusions or limitations")
    important_dates: Dict[str, str] = Field(description="Important dates (issue, expiry, etc.)")
    special_provisions: List[str] = Field(description="Special provisions or riders")

class PolicyExplainerOutput(BaseModel):
    """Output from the Policy Explainer Agent"""
    response: str = Field(description="Natural language explanation of policy details")
    policy_details: Optional[PolicyDetail] = Field(description="Structured policy details")
    document_references: List[Dict[str, str]] = Field(description="References to source documents")
    chain_of_thought: str = Field(description="Reasoning process used to analyze the policy")
    suggested_next_agent: Optional[str] = Field(description="Suggested next agent to handle the query")

# Create the policy explainer prompt
policy_explainer_system_prompt = """You are the Policy Explainer Agent, an expert in analyzing and explaining insurance policies.

Your role is to:

1. Retrieve and analyze insurance policy documents
2. Extract key policy details, terms, and conditions
3. Explain policy features in clear, simple language
4. Identify important provisions, exclusions, and limitations
5. Provide accurate and complete information about coverage

When answering questions about policies:
- Always ground your explanations in the specific policy documents
- Use precise language to avoid misinterpretation
- Highlight important exclusions or limitations
- Explain insurance terminology in simple terms
- Be transparent about what's covered and what's not

Focus on being accurate, thorough, and educational. Your explanations will be used by financial advisors to explain policies to their clients, so clarity and accuracy are essential.

If a specific policy document isn't available, clearly state this limitation and provide general information about similar policy types.
"""

policy_explainer_prompt = ChatPromptTemplate.from_messages([
    ("system", policy_explainer_system_prompt),
    ("human", """
Query: {query}

Client Profile:
{client_profile}

Policy Documents:
{policy_documents}

Please analyze these policy documents and provide a clear explanation that addresses the query.
""")
])

# Initialize the model
policy_explainer_model = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.1)

def policy_explainer_agent(state):
    """
    Policy Explainer agent that explains insurance policy details
    """
    # Check if this agent has already processed this query
    if "policy_explainer" in state["agent_outputs"]:
        # Agent has already run, don't run again
        return state
    
    # Extract the relevant information from the state
    messages = state["messages"]
    client_id = state["client_id"]
    human_messages = [m for m in messages if isinstance(m, HumanMessage)]
    current_query = human_messages[-1].content if human_messages else ""
    
    # Get client information
    client_info = client_db_tool(client_id=client_id)
    
    # Format client profile
    client_profile = f"""
Name: {client_info.get('name', 'Unknown')}
Age: {client_info.get('age', 'Unknown')}
Policies: {', '.join([p.get('name', 'Unknown') for p in client_info.get('policies', [])])}
"""
    
    # Retrieve relevant policy documents
    documents = document_retrieval_tool(
        query=current_query,
        client_id=client_id,
        document_type="policy"
    )
    
    # Format policy documents
    policy_documents = ""
    document_references = []
    
    if documents:
        for i, doc in enumerate(documents):
            policy_documents += f"\nDocument {i+1}: {doc.get('title', 'Unknown')}\n"
            policy_documents += f"Content:\n{doc.get('content', 'No content available')}\n"
            
            document_references.append({
                "id": doc.get("id", f"doc-{i+1}"),
                "title": doc.get("title", "Policy Document"),
                "type": "policy",
                "snippet": doc.get("content", "")[:150] + "..."
            })
    else:
        policy_documents = "No specific policy documents found for this query."
    
    # Prepare the input for the LLM
    input_values = {
        "query": current_query,
        "client_profile": client_profile,
        "policy_documents": policy_documents
    }
    
    # Generate the policy explanation
    try:
        llm_response = policy_explainer_model.invoke(policy_explainer_prompt.format(**input_values))
        response_text = llm_response.content
        
        # In a real implementation, you would parse the LLM output to extract policy details
        # For this mock implementation, we'll create plausible structured details
        
        policy_details = None
        if documents:
            # Extract some basic details from the first document
            doc = documents[0]
            content = doc.get('content', '')
            
            # Simple extraction for demonstration
            coverage = "$500,000" if "500,000" in content else "Not specified"
            premium = "$1,200/year" if "1,200" in content else "Not specified"
            
            # Extract some key benefits
            benefits = []
            if "Death Benefit" in content:
                benefits.append("Death benefit payable to beneficiaries")
            if "Conversion Option" in content:
                benefits.append("Option to convert to permanent life insurance")
            if "Renewability" in content:
                benefits.append("Renewable without evidence of insurability")
            if len(benefits) == 0:
                benefits = ["Policy provides financial protection", "Fixed premium for the term period"]
            
            # Extract some exclusions
            exclusions = []
            if "Exclusions" in content and "Suicide" in content:
                exclusions.append("Suicide within first 2 years")
            if "Material misrepresentation" in content:
                exclusions.append("Material misrepresentation in application")
            if "War" in content:
                exclusions.append("War or act of war")
            if len(exclusions) == 0:
                exclusions = ["Standard industry exclusions apply"]
            
            # Extract important dates
            dates = {}
            if "Issue Date:" in content:
                issue_date = content.split("Issue Date:")[1].split("\n")[0].strip()
                dates["Issue Date"] = issue_date
            if "Expiry Date:" in content:
                expiry_date = content.split("Expiry Date:")[1].split("\n")[0].strip()
                dates["Expiry Date"] = expiry_date
            
            if not dates:
                dates = {"Issue Date": "Not specified", "Expiry Date": "Not specified"}
            
            # Create structured policy details
            policy_details = PolicyDetail(
                policy_type="Term Life Insurance" if "Term Life" in doc.get('title', '') else "Insurance Policy",
                policy_name=doc.get('title', 'Unknown').replace(" - ", " for "),
                coverage_amount=coverage,
                premium=premium,
                key_benefits=benefits,
                exclusions=exclusions,
                important_dates=dates,
                special_provisions=["None specified"]
            )
        
        # Determine if we should suggest another agent
        suggested_next = None
        
        if not documents and "fund" in current_query.lower():
            suggested_next = "ilp_insights"
        elif "recommend" in current_query.lower() or "suitable" in current_query.lower():
            suggested_next = "product_suitability"
        elif "compliance" in current_query.lower():
            suggested_next = "compliance_check"
        
        # Create structured output
        chain_of_thought = "I analyzed the policy documents by extracting key terms, conditions, coverage details, and exclusions, then simplified the language for clarity while maintaining accuracy."
        
        output = {
            "response": response_text,
            "policy_details": policy_details.dict() if policy_details else None,
            "document_references": document_references,
            "chain_of_thought": chain_of_thought,
            "suggested_next_agent": suggested_next
        }
        
    except Exception as e:
        # Fallback response if LLM call fails
        print(f"Error in policy explainer agent: {str(e)}")
        
        response_text = "Based on the policy documents I've analyzed:\n\n"
        
        if documents:
            doc = documents[0]
            response_text += f"The {doc.get('title', 'policy')} provides the following key details:\n\n"
            
            content = doc.get('content', '')
            if "Coverage Amount:" in content:
                coverage = content.split("Coverage Amount:")[1].split("\n")[0].strip()
                response_text += f"- Coverage Amount: {coverage}\n"
            if "Premium:" in content:
                premium = content.split("Premium:")[1].split("\n")[0].strip()
                response_text += f"- Premium: {premium}\n"
            if "Exclusions" in content:
                response_text += "\nKey exclusions may apply. Please review the policy document for details.\n"
        else:
            response_text += "I couldn't find specific policy documents matching your query. Please provide more details about which policy you're interested in."
        
        # Create fallback output
        output = {
            "response": response_text,
            "policy_details": None,
            "document_references": document_references,
            "chain_of_thought": "Attempted to extract policy details from available documents.",
            "suggested_next_agent": "ilp_insights" if "fund" in current_query.lower() else None
        }
    
    # Add the response to messages
    messages.append(AIMessage(content=output["response"]))
    
    # Update the state
    state["messages"] = messages
    state["agent_path"].append("policy_explainer")
    state["agent_outputs"]["policy_explainer"] = output
    state["current_agent"] = "policy_explainer"
    
    # Save relevant information to shared memory
    if "shared_memory" not in state:
        state["shared_memory"] = {}
    
    if output["policy_details"]:
        state["shared_memory"]["policy_details"] = output["policy_details"]
    
    return state