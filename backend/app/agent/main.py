# backend/app/agent/main.py
from typing import Dict, List, Any, Literal, TypedDict, Union, Optional
from uuid import UUID
import json
import os
from datetime import datetime
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)

# Import agent implementations
from .agents.coordinator import coordinator_agent
from .agents.client_profiler import client_profiler_agent
from .agents.policy_explainer import policy_explainer_agent
from .agents.product_suitability import product_suitability_agent
from .agents.compliance_check import compliance_check_agent
from .agents.ilp_insights import ilp_insights_agent
from .agents.review_upsell import review_upsell_agent

# State definition
class AgentState(TypedDict):
    messages: List[Union[HumanMessage, AIMessage]]
    client_id: str  # Using string instead of UUID for easier mocking
    function_type: str
    agent_path: List[str]
    agent_outputs: Dict[str, Any]
    current_agent: str
    shared_memory: Dict[str, Any]
    final_response: Optional[str]

# Initialize LLMs with environment variables
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
MODEL_NAME = os.environ.get("LLM_MODEL_NAME", "gpt-3.5-turbo")

# Configure LLM instances - use a single model instance for all agents in production
model = ChatOpenAI(model=MODEL_NAME, temperature=0.1)

# Function to decide the next agent based on coordinator's routing decision
def decide_next_agent(state: AgentState) -> str:
    """Route to the next agent or end the process based on coordinator's decision"""
    if state["current_agent"] == "coordinator":
        next_agent = state["agent_outputs"]["coordinator"].get("next_agent")
        
        if next_agent == "END":
            return END
        elif next_agent in [
            "client_profiler", "policy_explainer", "product_suitability",
            "compliance_check", "ilp_insights", "review_upsell"
        ]:
            return next_agent
        else:
            # Default to ending if next_agent is invalid
            logger.warning(f"Invalid next_agent: {next_agent}. Ending conversation.")
            return END
    else:
        # After any other agent completes, return to coordinator
        return "coordinator"

# Build the agent graph
def build_agent_graph() -> StateGraph:
    """Construct the StateGraph for the multi-agent system"""
    workflow = StateGraph(AgentState)
    
    # Add nodes for each agent
    workflow.add_node("coordinator", coordinator_agent)
    workflow.add_node("client_profiler", client_profiler_agent)
    workflow.add_node("policy_explainer", policy_explainer_agent)
    workflow.add_node("product_suitability", product_suitability_agent)
    workflow.add_node("compliance_check", compliance_check_agent) 
    workflow.add_node("ilp_insights", ilp_insights_agent)
    workflow.add_node("review_upsell", review_upsell_agent)
    
    # Add conditional edges based on the routing logic
    workflow.add_conditional_edges(
        "coordinator",
        decide_next_agent
    )
    
    # Connect all other agents back to the coordinator
    for agent in [
        "client_profiler", "policy_explainer", "product_suitability",
        "compliance_check", "ilp_insights", "review_upsell"
    ]:
        workflow.add_edge(agent, "coordinator")
    
    # Set the entry point
    workflow.set_entry_point("coordinator")
    
    return workflow

# Initialize the agent graph
agent_graph = build_agent_graph().compile()

# Function to handle agent requests
async def handle_agent_request(query_request, client=None, conversation=None):
    """Process an agent query request with improved handling"""
    start_time = datetime.now()
    logger.info(f"Starting agent request processing: {start_time}")
    
    # Use mock client data if no client is provided
    if client is None:
        client_id = query_request.client_id if hasattr(query_request, 'client_id') else "client-1"
        # Import client_db_tool here to avoid circular imports
        from agent.tools import client_db_tool
        client = client_db_tool(client_id=client_id)
        logger.info(f"Using mock client data for client_id: {client_id}")
    else:
        # Extract client ID from the client object
        client_id = str(client.id) if hasattr(client, 'id') else "client-1"
        logger.info(f"Using provided client data for client_id: {client_id}")
    
    # Convert query_request to a dict if it's not already
    if hasattr(query_request, 'query'):
        query = query_request.query
        function_type = query_request.function_type if hasattr(query_request, 'function_type') else "needs-assessment"
    else:
        query = str(query_request)
        function_type = "needs-assessment"  # Default function type
    
    logger.info(f"Query: {query}")
    logger.info(f"Function type: {function_type}")
    
    # Get conversation history if available
    conversation_history = []
    if conversation and hasattr(conversation, 'messages') and conversation.messages:
        conversation_history = conversation.messages
        logger.info(f"Using existing conversation with {len(conversation_history)} messages")
    
    # Initialize the state
    initial_state: AgentState = {
        "messages": [HumanMessage(content=query)],
        "client_id": client_id,
        "function_type": function_type,
        "agent_path": [],
        "agent_outputs": {},
        "current_agent": "coordinator",
        "shared_memory": {
            "client_info": client,
            "conversation_history": conversation_history
        },
        "final_response": None
    }
    
    # Execute the agent workflow with a maximum number of steps to prevent infinite loops
    try:
        # Use the recursion_limit parameter to prevent infinite loops
        logger.info("Invoking agent graph")
        result = agent_graph.invoke(initial_state, {"recursion_limit": 10})
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        logger.info(f"Agent request processing completed in {duration:.2f} seconds")
        logger.info(f"Agent path: {' -> '.join(result['agent_path'])}")
        
        return result
    except Exception as e:
        logger.error(f"Error executing agent workflow: {str(e)}", exc_info=True)
        # Return a simple error response
        return {
            "messages": [HumanMessage(content=query), AIMessage(content=f"I encountered an error processing your request: {str(e)}")],
            "client_id": client_id,
            "function_type": function_type,
            "agent_path": ["coordinator"],
            "agent_outputs": {"error": str(e)},
            "current_agent": "coordinator",
            "shared_memory": {},
            "final_response": f"I encountered an error processing your request: {str(e)}"
        }

# Simple test function
def test_agent(query, client_id="client-1", function_type="needs-assessment"):
    """Test the agent with a simple query"""
    import asyncio
    
    class MockRequest:
        def __init__(self, query, client_id, function_type):
            self.query = query
            self.client_id = client_id
            self.function_type = function_type
    
    # Create a mock request
    request = MockRequest(query, client_id, function_type)
    
    # Process the request
    result = asyncio.run(handle_agent_request(request))
    
    # Print the result
    print("\n===== AGENT TEST RESULT =====")
    print(f"Query: {query}")
    print(f"Client ID: {client_id}")
    print(f"Function Type: {function_type}")
    print(f"Agent Path: {result['agent_path']}")
    
    # Print messages
    print("\nConversation:")
    for i, msg in enumerate(result["messages"]):
        sender = "Human" if isinstance(msg, HumanMessage) else "AI"
        content = msg.content
        if len(content) > 100:
            content = content[:100] + "..."
        print(f"{sender}: {content}")
    
    if result.get("final_response"):
        final_response = result["final_response"]
        if len(final_response) > 200:
            final_response = final_response[:200] + "..."
        print(f"\nFinal Response: {final_response}")
    
    print("\nAgent Path:")
    for agent in result["agent_path"]:
        if agent != "coordinator" and agent in result["agent_outputs"]:
            output = result["agent_outputs"][agent]
            print(f"\n{'-'*20} {agent.upper()} OUTPUT {'-'*20}")
            if "response" in output:
                response = output["response"]
                if len(response) > 200:
                    response = response[:200] + "..."
                print(f"Response: {response}")
            if "chain_of_thought" in output:
                chain = output["chain_of_thought"]
                if len(chain) > 100:
                    chain = chain[:100] + "..."
                print(f"Chain of Thought: {chain}")
            print(f"{'-'*60}")
    
    return result

# Run a test if executed directly
if __name__ == "__main__":
    test_queries = [
        ("Tell me about John Smith's life insurance policy", "client-1", "policy-explainer"),
        ("What are Sarah's financial needs?", "client-2", "needs-assessment"),
        ("What insurance products would you recommend for Emily?", "client-4", "product-recommendation"),
        ("How has the Global Growth Fund been performing?", "client-4", "policy-explainer")
    ]
    
    for query, client_id, function_type in test_queries:
        test_agent(query, client_id, function_type)
        print("\n" + "="*80 + "\n")