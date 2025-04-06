# backend/app/agent/test_coordinator.py
from agent.main_i import agent_graph
from typing import Dict, List, Any

# Test state
test_state = {
    "messages": [{"role": "human", "content": "Explain the client's term life policy"}],
    "client_id": "some-uuid",
    "function_type": "policy-explainer",
    "agent_path": [],
    "agent_outputs": {},
    "current_agent": "coordinator",
    "shared_memory": {
        "client_info": {"name": "John Smith"},
        "conversation_history": []
    },
    "final_response": None
}

# Run the test
result = agent_graph.invoke(test_state)
print("Next agent:", result["agent_outputs"]["coordinator"]["next_agent"])