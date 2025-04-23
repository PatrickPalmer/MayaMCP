
def list_objects_by_type(filter_by:str=None) -> list:
    """ Get a list of objects in the scene. Use filter_by to filter for 
        certain objects such as "cameras", "lights", "materials", or "shapes". """
    import maya.cmds as cmds
    if filter_by in ("object", "objects", "all", 'null', None):
        filter_by = "dag"
    args = { filter_by: True }
    return cmds.ls(**args) 

