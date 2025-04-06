# backend/app/agent/agents/coordinator.py
from typing import Dict, List, Any, TypedDict, Union, Optional
from langchain_core.messages import HumanMessage, AIMessage

# Function type to routing map
FUNCTION_TYPE_ROUTING = {
    "policy-explainer": "policy_explainer",
    "needs-assessment": "client_profiler",
    "product-recommendation": "product_suitability",
    "compliance-check": "compliance_check",
}

def coordinator_agent(state):
    """
    Coordinator agent that routes queries to specialized agents
    with improved response generation
    """
    # Extract the relevant information from the state
    messages = state["messages"]
    client_id = state["client_id"]
    function_type = state["function_type"]
    agent_path = state["agent_path"]
    agent_outputs = state["agent_outputs"]
    
    # Get the current query (the last message from the human)
    human_messages = [m for m in messages if isinstance(m, HumanMessage)]
    current_query = human_messages[-1].content if human_messages else ""
    
    # Initialize next_agent and reasoning
    next_agent = None
    reasoning = ""
    
    # Track which agents have already been used
    visited_agents = set()
    for agent in agent_path:
        if agent != "coordinator":
            visited_agents.add(agent)
    
    # Get the last non-coordinator agent in the path (if any)
    last_agent = None
    for agent in reversed(agent_path):
        if agent != "coordinator":
            last_agent = agent
            break
    
    # 1. Loop prevention - if we've cycled through agents too many times, end conversation
    if len(agent_path) >= 6:  # Coordinator + agent + coordinator + agent + coordinator (5 steps)
        next_agent = "END"
        reasoning = "Ending conversation after sufficient agent interactions"
    
    # 2. If this is the first routing decision
    elif not agent_path:
        # Direct routing based on function type
        if function_type in FUNCTION_TYPE_ROUTING:
            next_agent = FUNCTION_TYPE_ROUTING[function_type]
            reasoning = f"Initial routing based on function type: {function_type}"
        else:
            # Keyword-based routing
            next_agent = route_by_keywords(current_query)
            reasoning = f"Initial routing based on query keywords: {next_agent}"
    
    # 3. If we're in the middle of the conversation
    else:
        # Check if the last agent suggested a different agent to try
        suggested_next = None
        if last_agent and last_agent in agent_outputs:
            last_output = agent_outputs[last_agent]
            if "suggested_next_agent" in last_output:
                suggested_next = last_output["suggested_next_agent"]
        
        if suggested_next and suggested_next not in visited_agents:
            # Use the suggested agent if it hasn't been visited
            next_agent = suggested_next
            reasoning = f"Following suggestion from {last_agent} to route to {next_agent}"
        else:
            # Try to find a better agent based on the query
            query_based_agent = route_by_keywords(current_query)
            
            # Only switch if we haven't tried this agent yet
            if query_based_agent not in visited_agents:
                next_agent = query_based_agent
                reasoning = f"Re-routing based on query keywords: {next_agent}"
            else:
                # We've tried all relevant agents, end the conversation
                next_agent = "END"
                reasoning = "Ending conversation after trying all relevant agents"
    
    # Record the path
    new_agent_path = agent_path + ["coordinator"]
    
    # Create the result
    result = {
        "next_agent": next_agent,
        "reasoning": reasoning,
        "clarification_needed": False,
        "clarification_question": None
    }
    
    # Update the state
    state["agent_path"] = new_agent_path
    state["agent_outputs"]["coordinator"] = result
    state["current_agent"] = "coordinator"
    
    # If we're ending, prepare a final response
    if next_agent == "END":
        # Create a better final response
        final_response = generate_final_response(state, agent_outputs)
        state["final_response"] = final_response
    
    return state

def generate_final_response(state, agent_outputs):
    """
    Generate a coherent final response using the most relevant agent's output
    """
    # Identify the most relevant agent for this query
    relevant_agent = find_most_relevant_agent(state)
    
    if relevant_agent and relevant_agent in agent_outputs:
        # Use the most relevant agent's response
        return agent_outputs[relevant_agent].get("response", "I don't have specific information about that.")
    
    # Fallback to combining outputs if we couldn't identify a single most relevant agent
    final_response = ""
    used_responses = set()
    
    # Get a list of agents ordered by their appearance in the conversation
    agent_path = [a for a in state["agent_path"] if a != "coordinator"]
    
    # Track if we've already included content from certain agents
    included_agents = set()
    
    # First pass - add responses from agents in order of appearance
    for agent in agent_path:
        # Skip duplicates and coordinator
        if agent in included_agents or agent == "coordinator":
            continue
        
        if agent in agent_outputs and "response" in agent_outputs[agent]:
            response = agent_outputs[agent]["response"]
            # Check if this is a unique response
            response_key = response[:30]
            if response_key not in used_responses:
                used_responses.add(response_key)
                
                # Skip incomplete or error responses
                if "couldn't find" in response.lower() or "not found" in response.lower():
                    continue
                
                # Add to final response
                if final_response:
                    final_response += "\n\n"
                final_response += response
                included_agents.add(agent)
    
    # If we didn't find any good responses, use the last agent's response as fallback
    if not final_response and agent_path:
        last_agent = agent_path[-1]
        if last_agent in agent_outputs and "response" in agent_outputs[last_agent]:
            final_response = agent_outputs[last_agent]["response"]
    
    # If we still don't have a response, provide a generic one
    if not final_response:
        final_response = "I've analyzed your query but couldn't find specific information to address it. Could you provide more details?"
    
    return final_response

def find_most_relevant_agent(state):
    """
    Determine which agent's response is most relevant for the final answer
    """
    query = ""
    for msg in state["messages"]:
        if isinstance(msg, HumanMessage):
            query = msg.content
    
    query_lower = query.lower()
    agent_path = [a for a in state["agent_path"] if a != "coordinator"]
    
    # If we have no agents in the path, return None
    if not agent_path:
        return None
    
    # If the query specifically mentions fund performance and ilp_insights was used
    if any(term in query_lower for term in ["fund", "investment", "performance", "growth"]) and "ilp_insights" in agent_path:
        return "ilp_insights"
    
    # If the query asks about opportunities/upsell and review_upsell was used
    if any(term in query_lower for term in ["upsell", "opportunity", "review"]) and "review_upsell" in agent_path:
        return "review_upsell"
    
    # If the query asks about compliance and compliance_check was used
    if any(term in query_lower for term in ["compliance", "regulation", "rules"]) and "compliance_check" in agent_path:
        return "compliance_check"
    
    # If the query asks about products and product_suitability was used
    if any(term in query_lower for term in ["recommend", "product", "suitable"]) and "product_suitability" in agent_path:
        return "product_suitability"
    
    # If the query asks about a policy and policy_explainer was used
    if any(term in query_lower for term in ["policy", "insurance", "coverage"]) and "policy_explainer" in agent_path:
        return "policy_explainer"
    
    # Default to the last agent in the path
    return agent_path[-1]

def route_by_keywords(query):
    """Route to appropriate agent based on query keywords"""
    query_lower = query.lower()
    
    if any(word in query_lower for word in ["policy", "coverage", "insurance details", "term"]):
        return "policy_explainer"
    
    elif any(word in query_lower for word in ["needs", "profile", "assessment", "financial needs"]):
        return "client_profiler"
    
    elif any(word in query_lower for word in ["recommend", "product", "suitable", "suggestion"]):
        return "product_suitability"
    
    elif any(word in query_lower for word in ["compliance", "regulation", "rules", "requirements"]):
        return "compliance_check"
    
    elif any(word in query_lower for word in ["investment", "fund", "performance", "ilp", "growth"]):
        return "ilp_insights"
    
    elif any(word in query_lower for word in ["review", "upsell", "opportunity", "upgrade"]):
        return "review_upsell"
    
    # Default to client profiler
    return "client_profiler"