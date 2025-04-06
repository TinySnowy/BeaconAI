# backend/app/agent/utils.py

def safe_dict_access(obj, key, default=None):
    """
    Safely access an attribute or dictionary key regardless of whether
    the object is a Pydantic model, a dictionary, or something else.
    
    Args:
        obj: The object to access (Pydantic model, dict, or other)
        key: The attribute or key to access
        default: Default value if the key/attribute doesn't exist
    
    Returns:
        The value of the attribute/key or the default value
    """
    if obj is None:
        return default
    
    # Try attribute access for Pydantic models
    if hasattr(obj, key) and not isinstance(getattr(obj, key, None), type(obj).__class__):
        return getattr(obj, key)
    
    # Try dictionary access
    if isinstance(obj, dict) and key in obj:
        return obj[key]
    
    # Try dictionary get method
    if isinstance(obj, dict):
        return obj.get(key, default)
    
    # Default fallback
    return default

def safe_to_dict(obj):
    """
    Convert an object to a dictionary safely, handling Pydantic models,
    dictionaries, and lists of either.
    
    Args:
        obj: A Pydantic model, dictionary, list, or other object
        
    Returns:
        A dictionary representation of the object
    """
    # None handling
    if obj is None:
        return None
    
    # Pydantic model
    if hasattr(obj, 'dict') and callable(getattr(obj, 'dict')):
        return obj.dict()
    
    # Already a dictionary
    if isinstance(obj, dict):
        return obj
    
    # List handling - convert each item
    if isinstance(obj, list):
        return [safe_to_dict(item) for item in obj]
    
    # Fallback - try to convert to a dictionary using vars()
    try:
        return vars(obj)
    except:
        # Last resort
        return {"value": str(obj)}

def safe_list_to_dict(obj_list):
    """
    Convert a list of objects to a list of dictionaries
    
    Args:
        obj_list: A list of Pydantic models, dictionaries, or other objects
        
    Returns:
        A list of dictionaries
    """
    if obj_list is None:
        return []
    
    if not isinstance(obj_list, list):
        obj_list = [obj_list]
    
    return [safe_to_dict(item) for item in obj_list]