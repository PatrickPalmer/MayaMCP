

def clear_selection_list() -> None:
    """ Clears the user selection list of objects. """
    import maya.cmds as cmds
    cmds.select(clear=True)
