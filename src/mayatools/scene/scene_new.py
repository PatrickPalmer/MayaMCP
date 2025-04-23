
from typing import Dict, Any

def scene_new(force:bool=False) -> Dict[str, Any]:
    """ Create a new scene in Maya. Use the force argument to force a new scene when
        an existing scene is loaded and has been modified. """
    import maya.cmds as cmds
    try:
        cmds.file(new=True, force=force)

        # new scenes are marked as modified which can cause issues if you want to read in a file right away
        cmds.file(modified=False)

        results = { "success": True }
    except RuntimeError as e:
        if not force:
            raise RuntimeError("Unable to create a new scene because of unsaved changes. Use force to force a new scene.")
        else:
            raise RuntimeError("Unable to create a new scene")

    return results
