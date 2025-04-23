
from typing import Dict, Any, List


def set_object_transform_attributes(
    object_name:str, 
    translate:List[float]=None, 
    rotate:List[float]=None, 
    scale:List[float]=None
) -> Dict[str, Any]:
    """ set an objects transform attributes. Only specify which attribute needs to change.
        Arguments translate, rotate, and scale are a 3d vector and needs to be a list of
        3 floating point values. Rotate values are in degrees. """

    import maya.cmds as cmds

    def _validate_vector3d(vec:List[float]):
        return isinstance(vec, list) and len(vec) == 3 and all([isinstance(v, float) for v in vec])

    if not cmds.objExists(object_name):
        raise ValueError(f"{object_name} doesn't exist in the scene")
    if not cmds.attributeQuery('translate', node=object_name, exists=True):
        raise ValueError(f"{object_name} doesn't have any transform attributes")

    if not translate and not rotate and not scale:
        raise ValueError("Must set at least one of the transform values (translate, rotate, or scale).")
    if translate and not _validate_vector3d(translate):
        raise ValueError("Invalid translate format. Must be a list of 3 float values.")
    if rotate and not _validate_vector3d(rotate):
        raise ValueError("Invalid rotate format. Must be a list of 3 float values in degrees.")
    if scale and not _validate_vector3d(scale):
        raise ValueError("Invalid scale format. Must be a list of 3 float values.")

    try:
        if translate:
            cmds.setAttr(f'{object_name}.translate', translate[0], translate[1], translate[2], type="double3")
        if rotate:
            cmds.setAttr(f'{object_name}.rotate', rotate[0], rotate[1], rotate[2], type="double3")
        if scale:
            cmds.setAttr(f'{object_name}.scale', scale[0], scale[1], scale[2], type="double3")
        results = { "success": True }
    except Exception as e:
        raise RuntimeError(f"Unable to update the transform attributes on object_name {object_name}")

    return results
    
