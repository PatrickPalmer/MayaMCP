

def viewport_focus(object_name:str) -> None:
    """ Center and fit the viewport to focus on an object in the scene. 
        If object_name is set to None, all objects will be put into focus. """
    import maya.cmds as cmds
    if object_name:
        cmds.viewFit(object_name)
    else:
        cmds.viewFit(all=True)

