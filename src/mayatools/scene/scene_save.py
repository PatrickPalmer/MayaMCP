
import os
from typing import Dict, Any

def scene_save(filename:str=None) -> Dict[str, Any]:
    """ Save the current scene. If the filename is not specified, it will save it as its current name.
        If the current scene is not named, this call will fail. """
    import maya.cmds as cmds

    if not filename:
        filename = cmds.file(query=True, sceneName=True)
        if not filename:
            raise ValueError("Unable to save existing scene since it doesn't yet have a filename. Specify a filename to save scene.")

    file_type = None
    _, ext = os.path.splitext(filename)
    if ext == ".mb":
        file_type = "mayabinary"
    elif ext == ".ma":
        file_type = "mayaascii"
    elif not ext:
        # no extension
        file_type = cmds.file(query=True, type=True)
        if isinstance(file_type, list):
            if len(file_type) == 1:
                file_type = file_type[0]
            else:
                raise RuntimeError("Unable to determine the file type of the current scene")
        ext = ".mb" if file_type == "mayabinary" else ".ma"
        filename += ext
    else:
        # trying to save a format that should be export
        # future to support FBX, USD
        raise ValueError(f"Error: Unable to export a scene in the file format {ext}")

    if file_type:
        cmds.file(rename=filename)
        cmds.file(save=True, type=file_type)
        results = { "success": True }

    return results
