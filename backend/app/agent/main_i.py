# backend/app/agent/main.py
from typing import Dict, List, Any, Literal, TypedDict, Union, Optional, Annotated
from uuid import UUID
import json
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

# Import tool implementations
from agent.tools_i import (
    document_retrieval_tool,
    client_db_tool,
    product_db_tool,
    compliance_rules_tool,
    market_data_tool
)

# State definition
class AgentState(TypedDict):
    messages: List[Union[HumanMessage, AIMessage]]
    client_id: Optional[UUID]
    function_type: str
    agent_path: List[str]
    agent_outputs: Dict[str, Any]
    current_agent: str
    shared_memory: Dict[str, Any]
    final_response: Optional[str]

# Agent configuration with LLM instances
model = ChatOpenAI(model="gpt-4")
profiler_llm = ChatOpenAI(model="gpt-4", temperature=0.1)
explainer_llm = ChatOpenAI(model="gpt-4", temperature=0.1)
suitability_llm = ChatOpenAI(model="gpt-4", temperature=0.1)
compliance_llm = ChatOpenAI(model="gpt-4", temperature=0.1)
ilp_llm = ChatOpenAI(model="gpt-4", temperature=0.1)
review_llm = ChatOpenAI(model="gpt-4", temperature=0.1)

# Agent implementations
from app.agent.agents.coordinator import coordinator_agent
from app.agent.agents.client_profiler import client_profiler_agent
from app.agent.agents.policy_explainer import policy_explainer_agent
from app.agent.agents.product_suitability import product_suitability_agent
from app.agent.agents.compliance_check import compliance_check_agent
from app.agent.agents.ilp_insights import ilp_insights_agent
from app.agent.agents.review_upsell import review_upsell_agent

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
    
    # Add edges based on the routing logic
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

# Function to handle agent requests from the API
async def handle_agent_request(query_request, client, conversation):
    """Process an agent query request"""
    # Initialize the state
    initial_state: AgentState = {
        "messages": [HumanMessage(content=query_request.query)],
        "client_id": query_request.client_id,
        "function_type": query_request.function_type,
        "agent_path": [],
        "agent_outputs": {},
        "current_agent": "coordinator",
        "shared_memory": {
            "client_info": client.__dict__,
            "conversation_history": conversation.messages if conversation else []
        },
        "final_response": None
    }
    
    # Execute the agent workflow
    result = agent_graph.invoke(initial_state)
    
    # Process and return the response
    return result