
# get the objects attributes
# if the object is a transform, only return a subset
# if the transform is parent to a shape, include the shapes attributes as well

from typing import Dict, Any

def get_object_attributes(object_name:str) -> Dict[str, Any]:
    """ Get a list of attributes on a Maya object. If the object type is a transform and it the
        transform for a shape, the shape attributes are returned as well. """
    import maya.cmds as cmds

    def _get_attribute_values(attrs, results):
        for attr in attrs:
            if attr in results:
                continue
            if attr[-1] in ('X', 'Y', 'Z', 'R', 'G', 'B', 'A'):
                continue
            try:
                results[attr] = cmds.getAttr(f"{object_name}.{attr}")
                if isinstance(results[attr], list) and len(results[attr]) == 1:
                    results[attr] = results[attr][0]
            except:
                pass

    if not cmds.objExists(object_name):
        return { 
            "success": False,
            "message": f"Error: {object_name} doesn't exist in the scene"
        }

    results = {'name': object_name}

    # for transforms, only return a limited subset of the attributes
    if cmds.objectType(object_name) == 'transform':
        # get any attributes on the transform the user has added
        attrs = cmds.listAttr(object_name, userDefined=True) or []
        attrs.extend(['translate', 'rotate', 'scale', 'visibility', 'rotateOrder'])
    else:
        attrs = cmds.listAttr(object_name, read=True, visible=True) or []

    _get_attribute_values(attrs, results)

    # if transform, see if its a transform for a shape
    # if so, include the attributes of the shape as well
    if cmds.objectType(object_name) == 'transform':
        shapes = cmds.listRelatives(object_name, shapes=True)
        if shapes and len(shapes) >= 1:
            attrs = cmds.listAttr(shapes[0], read=True, visible=True) or []
            _get_attribute_values(attrs, results)

    return results
