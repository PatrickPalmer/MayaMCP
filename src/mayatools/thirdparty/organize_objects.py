from typing import Dict, List, Any, Optional, Union


def organize_objects(
    operation: str,
    objects: List[str],
    name: str = None,
    parameters: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Organize objects in the scene through grouping, parenting, or layout operations.
    
    Available operations:
    - group: Create a new group containing the specified objects
    - parent: Parent objects to the first object in the list
    - layout: Arrange objects in a grid, line, circle, or other pattern
    - center_pivot: Center the pivot point on each object
    - align: Align objects to each other or to world axis
    - distribute: Distribute objects evenly along an axis
    
    objects: List of object names to organize
    
    Parameters: Dictionary of operation-specific parameters
    Example for layout: {'pattern': 'grid', 'spacing': 5.0}
    Example for align: {'axis': 'x', 'align_to': 'min'}
    """
    import maya.cmds as cmds
    import random
    import math
    
    # Validate input objects
    for obj in objects:
        if not cmds.objExists(obj):
            raise ValueError(f"Object {obj} does not exist")
    
    # Set default parameters dict if none provided
    if parameters is None:
        parameters = {}
    
    # Set default name if none provided
    if name is None:
        name = f"{operation}_{int(random.random() * 1000)}"
    
    # Perform the requested operation
    if operation.lower() == "group":
        # Create a new group containing the objects
        group = cmds.group(objects, name=name)
        
        return {
            "success": True,
            "name": group,
            "operation": "group",
            "objects": objects
        }
    
    elif operation.lower() == "parent":
        if len(objects) < 2:
            raise ValueError("Parent operation requires at least two objects: parent and child(ren)")
        
        parent = objects[0]
        children = objects[1:]
        
        # Parent children to the parent
        cmds.parent(children, parent)
        
        return {
            "success": True,
            "name": parent,
            "operation": "parent",
            "parent": parent,
            "children": children
        }
    
    elif operation.lower() == "layout":
        if len(objects) < 1:
            raise ValueError("Layout operation requires at least one object")
        
        # Get layout parameters
        pattern = parameters.get('pattern', 'grid').lower()
        spacing = parameters.get('spacing', 5.0)
        
        # Get current positions for all objects
        positions = {}
        for obj in objects:
            pos = cmds.xform(obj, query=True, worldSpace=True, translation=True)
            positions[obj] = pos
        
        # Perform layout based on pattern
        if pattern == "grid":
            # Calculate grid dimensions
            grid_size = int(math.ceil(math.sqrt(len(objects))))
            
            for i, obj in enumerate(objects):
                row = i // grid_size
                col = i % grid_size
                
                x = col * spacing
                z = row * spacing
                
                # Keep original Y position
                y = positions[obj][1]
                
                cmds.move(x, y, z, obj, absolute=True)
                
        elif pattern == "line":
            # Get layout axis
            axis = parameters.get('axis', 'x').lower()
            
            for i, obj in enumerate(objects):
                if axis == 'x':
                    x = i * spacing
                    y = positions[obj][1]
                    z = positions[obj][2]
                elif axis == 'y':
                    x = positions[obj][0]
                    y = i * spacing
                    z = positions[obj][2]
                else:  # z
                    x = positions[obj][0]
                    y = positions[obj][1]
                    z = i * spacing
                
                cmds.move(x, y, z, obj, absolute=True)
                
        elif pattern == "circle":
            # Get circle parameters
            radius = parameters.get('radius', spacing * len(objects) / (2 * math.pi))
            axis = parameters.get('axis', 'y').lower()
            
            for i, obj in enumerate(objects):
                angle = 2.0 * math.pi * i / len(objects)
                
                if axis == 'y':
                    x = radius * math.cos(angle)
                    y = positions[obj][1]
                    z = radius * math.sin(angle)
                elif axis == 'x':
                    x = positions[obj][0]
                    y = radius * math.cos(angle)
                    z = radius * math.sin(angle)
                else:  # z
                    x = radius * math.cos(angle)
                    y = radius * math.sin(angle)
                    z = positions[obj][2]
                
                cmds.move(x, y, z, obj, absolute=True)
                
        else:
            raise ValueError(f"Unknown layout pattern: {pattern}. Use grid, line, or circle")
        
        # Group the objects if requested
        if parameters.get('create_group', False):
            group = cmds.group(objects, name=name)
            return {
                "success": True,
                "name": group,
                "operation": "layout",
                "pattern": pattern,
                "objects": objects
            }
        
        return {
            "success": True,
            "operation": "layout",
            "pattern": pattern,
            "objects": objects
        }
    
    elif operation.lower() == "center_pivot":
        # Center the pivot point on each object
        for obj in objects:
            cmds.xform(obj, centerPivots=True)
        
        return {
            "success": True,
            "operation": "center_pivot",
            "objects": objects
        }
    
    elif operation.lower() == "align":
        if len(objects) < 2:
            raise ValueError("Align operation requires at least two objects")
        
        # Get align parameters
        axis = parameters.get('axis', 'x').lower()
        align_to = parameters.get('align_to', 'min').lower()
        
        # Determine align positions for all objects
        positions = {}
        min_pos = float('inf')
        max_pos = float('-inf')
        
        # First pass: collect positions and find min/max
        for obj in objects:
            bbox = cmds.xform(obj, query=True, worldSpace=True, boundingBox=True)
            
            if axis == 'x':
                min_val = bbox[0]
                max_val = bbox[3]
            elif axis == 'y':
                min_val = bbox[1]
                max_val = bbox[4]
            else:  # z
                min_val = bbox[2]
                max_val = bbox[5]
            
            positions[obj] = {
                'min': min_val,
                'max': max_val,
                'center': (min_val + max_val) / 2.0
            }
            
            min_pos = min(min_pos, min_val)
            max_pos = max(max_pos, max_val)
        
        # Second pass: align objects
        target_pos = 0
        if align_to == 'min':
            target_pos = min_pos
        elif align_to == 'max':
            target_pos = max_pos
        elif align_to == 'center':
            target_pos = (min_pos + max_pos) / 2.0
        elif align_to == 'first':
            first_obj = objects[0]
            target_pos = positions[first_obj]['center']
        else:
            raise ValueError(f"Unknown align_to value: {align_to}. Use min, max, center, or first")
        
        # Move objects to align
        for obj in objects:
            current_pos = cmds.xform(obj, query=True, worldSpace=True, translation=True)
            
            if axis == 'x':
                offset = target_pos - positions[obj][align_to]
                cmds.move(offset, 0, 0, obj, relative=True)
            elif axis == 'y':
                offset = target_pos - positions[obj][align_to]
                cmds.move(0, offset, 0, obj, relative=True)
            else:  # z
                offset = target_pos - positions[obj][align_to]
                cmds.move(0, 0, offset, obj, relative=True)
        
        return {
            "success": True,
            "operation": "align",
            "axis": axis,
            "align_to": align_to,
            "objects": objects
        }
    
    elif operation.lower() == "distribute":
        if len(objects) < 3:
            raise ValueError("Distribute operation requires at least three objects")
        
        # Get distribute parameters
        axis = parameters.get('axis', 'x').lower()
        
        # First pass: collect center positions and find min/max
        positions = {}
        objects_by_pos = []
        
        for obj in objects:
            bbox = cmds.xform(obj, query=True, worldSpace=True, boundingBox=True)
            
            # Get center position based on axis
            if axis == 'x':
                center = (bbox[0] + bbox[3]) / 2.0
            elif axis == 'y':
                center = (bbox[1] + bbox[4]) / 2.0
            else:  # z
                center = (bbox[2] + bbox[5]) / 2.0
            
            positions[obj] = center
            objects_by_pos.append((obj, center))
        
        # Sort objects by position
        objects_by_pos.sort(key=lambda x: x[1])
        sorted_objects = [x[0] for x in objects_by_pos]
        
        # Get first and last object positions
        first_obj = sorted_objects[0]
        last_obj = sorted_objects[-1]
        start_pos = positions[first_obj]
        end_pos = positions[last_obj]
        total_distance = end_pos - start_pos
        
        # Calculate equal spacing
        if len(objects) > 2:
            spacing = total_distance / (len(objects) - 1)
            
            # Move objects to distributed positions
            for i, obj in enumerate(sorted_objects[1:-1], 1):
                target_pos = start_pos + i * spacing
                current_pos = positions[obj]
                offset = target_pos - current_pos
                
                if axis == 'x':
                    cmds.move(offset, 0, 0, obj, relative=True)
                elif axis == 'y':
                    cmds.move(0, offset, 0, obj, relative=True)
                else:  # z
                    cmds.move(0, 0, offset, obj, relative=True)
        
        return {
            "success": True,
            "operation": "distribute",
            "axis": axis,
            "objects": objects
        }
    
    else:
        raise ValueError(f"Unknown operation: {operation}. Use group, parent, layout, center_pivot, align, or distribute")