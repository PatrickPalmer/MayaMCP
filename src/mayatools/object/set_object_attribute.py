

# set an objects attribute
# if the object is a transform for a shape, the attribute may for the shape

from typing import Dict, Any, List


def set_object_attribute(object_name:str, attribute_name:str, attribute_value:Any) -> Dict[str, Any]:
    """ Set an object's attribute with a specific value. """
    import maya.cmds as cmds

    def _validate_vector3d(vec:List[float]):
        return isinstance(vec, list) and len(vec) == 3 and all([isinstance(v, float) for v in vec])

    if not cmds.objExists(object_name):
        raise ValueError(f"Error: {object_name} doesn't exist in the scene")

    if not cmds.attributeQuery(attribute_name, node=object_name, exists=True):
        # if the attribute doesn't exist, may exist on the child shape
        exist_on_shape = False
        if cmds.objectType(object_name) == 'transform':
            shapes = cmds.listRelatives(object_name, shapes=True)
            if shapes and len(shapes) >= 1:
                if cmds.attributeQuery(attribute_name, node=shapes[0], exists=True):
                    exist_on_shape = True
                    object_name = shapes[0]
        if not exist_on_shape:
            raise ValueError(f"Error: attribute {attribute_name} doesn't exist on {object_name}")

    attr_type = cmds.getAttr(f'{object_name}.{attribute_name}', type=True)
     
    if attr_type == 'double3':
        if not _validate_vector3d(attribute_value):
            raise ValueError(f"{attribute_name} is a 3d vector and needs to be list of 3 floats.")

    try:
        if attr_type == 'double3':
            cmds.setAttr(f'{object_name}.{attribute_name}', attribute_value[0], attribute_value[1], attribute_value[2], type=attr_type)
        elif attr_type == 'bool':
            cmds.setAttr(f'{object_name}.{attribute_name}', 1 if attribute_value else 0)
        else:
            cmds.setAttr(f'{object_name}.{attribute_name}', attribute_value)
        results = { "success": True }
    except Exception as e:
        raise RuntimeError(f"Error: Unable to update attribute {attribute_name} on object {object_name}")

    return results
    
