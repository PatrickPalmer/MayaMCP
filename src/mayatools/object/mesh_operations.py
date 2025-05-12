from typing import Dict, List, Any, Union, Optional


def mesh_operations(
    object_name: str,
    operation: str,
    parameters: Dict[str, Any] = None,
    select_components: Union[str, List[str]] = None
) -> Dict[str, Any]:
    """Perform mesh modeling operations on a polygon object.
    
    Available operations:
    - extrude: Extrude selected faces along their normals
    - bevel: Create a bevel on selected edges
    - subdivide: Subdivide the mesh to create more resolution
    - smooth: Apply smooth operation to the mesh
    - boolean: Perform boolean operations between two meshes
    - combine: Combine multiple meshes into one
    - bridge: Create a bridge between selected edges or faces
    - split: Split the mesh based on a plane
    
    Parameters is a dictionary containing operation-specific settings.
    Example parameters for extrude: {'distance': 1.0, 'divisions': 1}
    Example parameters for bevel: {'width': 0.2, 'segments': 2}
    Example parameters for boolean: {'target': 'target_object_name', 'operation': 'union'} 
                                    (operations: union, difference, intersection)
    
    select_components can be a string or list of strings identifying components to operate on,
    such as "pCube1.f[1:4]" for faces 1-4 on pCube1 or ["pCube1.e[1]", "pCube1.e[3]"] for edges 1 and 3.
    """
    import maya.cmds as cmds
    import maya.mel as mel
    
    # Validate inputs
    if not cmds.objExists(object_name):
        raise ValueError(f"Error: {object_name} doesn't exist in the scene")
    
    if cmds.objectType(object_name) != 'transform' and not cmds.objectType(object_name).startswith('mesh'):
        shape_node = cmds.listRelatives(object_name, shapes=True)
        if not shape_node or cmds.objectType(shape_node[0]) != 'mesh':
            raise ValueError(f"Error: {object_name} is not a polygon mesh")
    
    # Set default parameters dict if none provided
    if parameters is None:
        parameters = {}
    
    # Clear selection and then select the appropriate components
    cmds.select(clear=True)
    
    # Handle component selection if specified
    if select_components:
        if isinstance(select_components, list):
            for component in select_components:
                cmds.select(component, add=True)
        else:
            cmds.select(select_components)
    else:
        # Just select the entire object if no components specified
        cmds.select(object_name)
    
    # Perform the requested operation
    result = {"success": True, "object_name": object_name, "operation": operation}
    
    if operation.lower() == "extrude":
        # Get extrude parameters
        distance = parameters.get('distance', 1.0)
        divisions = parameters.get('divisions', 1)
        
        # Check if any components are selected
        selection = cmds.ls(selection=True)
        if not selection:
            raise ValueError("No valid components selected for extrude operation")
            
        # Determine if we're extruding faces or edges
        if '.f[' in str(selection):
            # Extrude faces
            result["extruded_faces"] = cmds.polyExtrudeFacet(
                constructionHistory=True,
                divisions=divisions,
                localTranslate=[0, distance, 0]
            )
        elif '.e[' in str(selection):
            # Extrude edges
            result["extruded_edges"] = cmds.polyExtrudeEdge(
                constructionHistory=True,
                divisions=divisions,
                localTranslate=[0, distance, 0]
            )
        else:
            raise ValueError("Selected components must be faces or edges for extrude operation")
    
    elif operation.lower() == "bevel":
        # Get bevel parameters
        width = parameters.get('width', 0.2)
        segments = parameters.get('segments', 2)
        
        # Check if any components are selected
        selection = cmds.ls(selection=True)
        if not selection:
            raise ValueError("No valid components selected for bevel operation")
            
        # Determine if we're beveling edges or vertices
        if '.e[' in str(selection):
            # Bevel edges
            result["beveled_edges"] = cmds.polyBevel3(
                fraction=width,
                segments=segments,
                constructionHistory=True
            )
        elif '.vtx[' in str(selection):
            # Bevel vertices
            result["beveled_vertices"] = cmds.polyBevel3(
                fraction=width,
                segments=segments,
                constructionHistory=True
            )
        else:
            raise ValueError("Selected components must be edges or vertices for bevel operation")
    
    elif operation.lower() == "subdivide":
        # Get subdivide parameters
        divisions = parameters.get('divisions', 1)
        
        # Apply subdivision
        result["subdivided"] = cmds.polySubdivideFacet(
            divisions=divisions
        )
    
    elif operation.lower() == "smooth":
        # Get smooth parameters
        divisions = parameters.get('divisions', 1)
        
        # Apply smoothing
        result["smoothed"] = cmds.polySmooth(
            divisions=divisions,
            constructionHistory=True
        )
    
    elif operation.lower() == "boolean":
        # Get boolean parameters
        target = parameters.get('target', None)
        operation_type = parameters.get('operation', 'union')
        
        if not target:
            raise ValueError("Target object must be specified for boolean operation")
        
        if not cmds.objExists(target):
            raise ValueError(f"Target object {target} doesn't exist in the scene")
        
        # Map operation type to Maya's boolean operation number
        op_map = {
            'union': 1,
            'difference': 2,
            'intersection': 3
        }
        
        if operation_type.lower() not in op_map:
            raise ValueError(f"Unknown boolean operation: {operation_type}. Use union, difference, or intersection")
        
        # Perform the boolean operation
        result["boolean_result"] = cmds.polyCBoolOp(
            object_name,
            target,
            op=op_map[operation_type.lower()],
            name=f"{object_name}_boolean"
        )[0]
    
    elif operation.lower() == "combine":
        # Get combine parameters
        targets = parameters.get('targets', [])
        
        if not targets:
            raise ValueError("Target objects must be specified for combine operation")
        
        # Validate all targets exist
        for target in targets:
            if not cmds.objExists(target):
                raise ValueError(f"Target object {target} doesn't exist in the scene")
        
        # Combine the objects
        objects_to_combine = [object_name] + targets
        result["combined"] = cmds.polyUnite(
            objects_to_combine,
            name=f"{object_name}_combined",
            constructionHistory=True
        )[0]
    
    elif operation.lower() == "bridge":
        # Get bridge parameters
        divisions = parameters.get('divisions', 1)
        twist = parameters.get('twist', 0)
        
        # Check if any components are selected
        selection = cmds.ls(selection=True)
        if not selection:
            raise ValueError("No valid components selected for bridge operation")
            
        # Bridge the selected components
        result["bridged"] = cmds.polyBridge(
            divisions=divisions,
            twist=twist,
            constructionHistory=True
        )
    
    elif operation.lower() == "split":
        # Get split parameters
        axis = parameters.get('axis', 'y')
        position = parameters.get('position', 0.0)
        
        # Validate the axis
        if axis.lower() not in ['x', 'y', 'z']:
            raise ValueError(f"Invalid axis: {axis}. Must be x, y, or z")
            
        # Create a cutting plane
        plane_pos = [0, 0, 0]
        plane_normal = [0, 0, 0]
        
        if axis.lower() == 'x':
            plane_pos[0] = position
            plane_normal[0] = 1
        elif axis.lower() == 'y':
            plane_pos[1] = position
            plane_normal[1] = 1
        else:  # z
            plane_pos[2] = position
            plane_normal[2] = 1
            
        # Split the mesh
        result["split_result"] = cmds.polyCut(
            object_name,
            ch=True,
            pc=plane_pos,
            ro=plane_normal,
            name=f"{object_name}_split"
        )
    
    else:
        raise ValueError(f"Unknown operation: {operation}. Use extrude, bevel, subdivide, smooth, boolean, combine, bridge, or split")
    
    return result