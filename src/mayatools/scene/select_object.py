
from typing import Dict, Any

def select_object(object_name:str) -> Dict[str, Any]:
    """ Select an object in the scene. """
    import maya.cmds as cmds

    try:
        cmds.select(object_name)
    except:
        raise ValueError(f"Error: {object_name} does not exist in the scene")

    return {'success': True}

