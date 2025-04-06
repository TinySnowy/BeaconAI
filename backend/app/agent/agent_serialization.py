# backend/app/agent/agent_serialization.py

from typing import Dict, List, Any, Optional, Union
from pydantic import BaseModel

def serialize_agent_output(output: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert all Pydantic models in agent outputs to dictionaries
    to ensure proper JSON serialization.
    
    This function should be called before returning outputs from any agent.
    
    Args:
        output: The original agent output dictionary
        
    Returns:
        A serializable version of the agent output
    """
    # Create a new dictionary for the result
    serialized = {}
    
    # Process each key in the output
    for key, value in output.items():
        serialized[key] = _serialize_value(value)
    
    return serialized

def _serialize_value(value: Any) -> Any:
    """
    Recursively serialize a value to ensure it's JSON serializable
    
    Args:
        value: Any value to serialize
        
    Returns:
        A serializable version of the value
    """
    # None handling
    if value is None:
        return None
    
    # Pydantic model
    if isinstance(value, BaseModel):
        return value.dict()
    
    # List handling
    if isinstance(value, list):
        return [_serialize_value(item) for item in value]
    
    # Dict handling
    if isinstance(value, dict):
        return {k: _serialize_value(v) for k, v in value.items()}
    
    # Other types are assumed to be already serializable
    return value

# Example usage at the end of each agent:
# output = serialize_agent_output({
#     "response": response_text,
#     "needs_assessment": needs_assessment,  # Pydantic model
#     "document_references": document_references,
#     "suggested_next_agent": suggested_next
# })