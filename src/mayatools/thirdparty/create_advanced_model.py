from typing import Dict, List, Any, Optional


def create_advanced_model(
    model_type: str,
    name: str = None,
    scale: float = 1.0,
    translate: List[float] = [0.0, 0.0, 0.0],
    rotate: List[float] = [0.0, 0.0, 0.0],
    color: List[float] = [0.5, 0.5, 0.5],
    parameters: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Creates an advanced model in the Maya scene.
    
    Available model types:
    - car: Creates a simple car model with body, wheels, windows
    - tree: Creates a tree with trunk and foliage
    - building: Creates a simple building with windows
    - cup: Creates a cup/mug model
    - chair: Creates a simple chair model
    
    Parameters is a dictionary that can contain specific settings for each model type.
    Example parameters for car: {'wheels': 4, 'sporty': True, 'convertible': False}
    Example parameters for tree: {'branches': 3, 'leaf_density': 0.8, 'type': 'pine'}
    
    Scale applies a uniform scale to the entire model.
    Translate positions the model in world space.
    Rotate values are in degrees.
    Color applies an initial material color (RGB values between 0-1).
    """
    import maya.cmds as cmds
    import random
    import math
    
    def _validate_vector3d(vec:List[float]):
        return isinstance(vec, list) and len(vec) == 3 and all([isinstance(v, float) for v in vec])
    
    # Input validation
    if not _validate_vector3d(translate):
        raise ValueError("Invalid translate format. Must be a list of 3 float values.")
    if not _validate_vector3d(rotate):
        raise ValueError("Invalid rotate format. Must be a list of 3 float values.")
    if not _validate_vector3d(color):
        raise ValueError("Invalid color format. Must be a list of 3 float values between 0-1.")
        
    # Set default parameters dict if none provided
    if parameters is None:
        parameters = {}
    
    # Set default name if none provided
    if name is None:
        name = f"{model_type}_{int(random.random() * 1000)}"
    
    # Create a group for the entire model
    model_group = cmds.group(empty=True, name=name)
    
    # Create a Lambert material for the model
    mat_name = f"{name}_material"
    material = cmds.shadingNode('lambert', asShader=True, name=mat_name)
    cmds.setAttr(f"{mat_name}.color", color[0], color[1], color[2], type='double3')
    
    # Function to apply transformations to the entire model at the end
    def finalize_model():
        # Apply scale to the group
        cmds.setAttr(f"{model_group}.scale", scale, scale, scale, type="double3")
        # Apply translate to the group
        cmds.setAttr(f"{model_group}.translate", translate[0], translate[1], translate[2], type="double3")
        # Apply rotate to the group
        cmds.setAttr(f"{model_group}.rotate", rotate[0], rotate[1], rotate[2], type="double3")
        
        return {
            "success": True,
            "name": model_group,
            "model_type": model_type,
            "components": components,
            "translate": translate,
            "rotate": rotate,
            "scale": scale
        }
    
    # Track components for return value
    components = []
    
    # Create a simple car model
    if model_type.lower() == "car":
        # Get car-specific parameters with defaults
        wheels = parameters.get('wheels', 4)
        sporty = parameters.get('sporty', False)
        convertible = parameters.get('convertible', False)
        
        # Create car body
        if sporty:
            # Sporty car body - lower and sleeker
            body = cmds.polyCube(w=2.0, h=0.5, d=4.0, name=f"{name}_body")[0]
            cmds.move(0, 0.6, 0, body)
            # Make it more aerodynamic with a wedge shape
            cmds.select(f"{body}.f[1]")  # Front face
            cmds.move(0, 0.2, 0, relative=True)
        else:
            # Standard car body
            body = cmds.polyCube(w=1.8, h=0.8, d=4.0, name=f"{name}_body")[0]
            cmds.move(0, 0.7, 0, body)
        
        components.append(body)
        cmds.parent(body, model_group)
        
        # Create cabin/roof unless it's a convertible
        if not convertible:
            cabin_height = 0.4 if sporty else 0.7
            cabin_width = 1.6 if sporty else 1.7
            cabin = cmds.polyCube(w=cabin_width, h=cabin_height, d=2.0, name=f"{name}_cabin")[0]
            cabin_y_pos = 1.15 if sporty else 1.6
            cmds.move(0, cabin_y_pos, -0.2, cabin)
            components.append(cabin)
            cmds.parent(cabin, model_group)
        
        # Create wheels
        wheel_radius = 0.4
        wheel_width = 0.2
        wheel_positions = []
        
        if wheels == 4:
            # Standard 4 wheels
            wheel_positions = [
                [-0.9, wheel_radius, 1.5],  # Front left
                [0.9, wheel_radius, 1.5],   # Front right
                [-0.9, wheel_radius, -1.5], # Rear left
                [0.9, wheel_radius, -1.5]   # Rear right
            ]
        elif wheels == 6:
            # 6 wheels (3 per side)
            wheel_positions = [
                [-0.9, wheel_radius, 1.5],   # Front left
                [0.9, wheel_radius, 1.5],    # Front right
                [-0.9, wheel_radius, 0],     # Middle left
                [0.9, wheel_radius, 0],      # Middle right
                [-0.9, wheel_radius, -1.5],  # Rear left
                [0.9, wheel_radius, -1.5]    # Rear right
            ]
        
        for i, pos in enumerate(wheel_positions):
            wheel = cmds.polyCylinder(r=wheel_radius, h=wheel_width, ax=(1, 0, 0), name=f"{name}_wheel_{i}")[0]
            cmds.move(pos[0], pos[1], pos[2], wheel)
            components.append(wheel)
            cmds.parent(wheel, model_group)
        
        # Create windows (if not convertible)
        if not convertible:
            # Windshield
            windshield = cmds.polyCube(w=1.4, h=0.5, d=0.1, name=f"{name}_windshield")[0]
            windshield_y = 1.35 if sporty else 1.6
            windshield_z = 0.6 if sporty else 0.7
            cmds.move(0, windshield_y, windshield_z, windshield)
            cmds.rotate(45, 0, 0, windshield)
            
            # Rear window
            rear_window = cmds.polyCube(w=1.4, h=0.5, d=0.1, name=f"{name}_rear_window")[0]
            rear_window_y = 1.35 if sporty else 1.6
            rear_window_z = -0.6 if sporty else -0.7
            cmds.move(0, rear_window_y, rear_window_z, rear_window)
            cmds.rotate(-45, 0, 0, rear_window)
            
            components.append(windshield)
            components.append(rear_window)
            cmds.parent(windshield, model_group)
            cmds.parent(rear_window, model_group)
            
            # Side windows
            side_window_l = cmds.polyCube(w=0.1, h=0.4, d=1.4, name=f"{name}_side_window_l")[0]
            side_window_r = cmds.polyCube(w=0.1, h=0.4, d=1.4, name=f"{name}_side_window_r")[0]
            side_window_y = 1.3 if sporty else 1.5
            cmds.move(-0.85, side_window_y, 0, side_window_l)
            cmds.move(0.85, side_window_y, 0, side_window_r)
            
            components.append(side_window_l)
            components.append(side_window_r)
            cmds.parent(side_window_l, model_group)
            cmds.parent(side_window_r, model_group)
        
        # Create headlights
        headlight_l = cmds.polyCylinder(r=0.2, h=0.1, ax=(1, 0, 0), name=f"{name}_headlight_l")[0]
        headlight_r = cmds.polyCylinder(r=0.2, h=0.1, ax=(1, 0, 0), name=f"{name}_headlight_r")[0]
        headlight_y = 0.7 if sporty else 0.8
        cmds.move(-0.7, headlight_y, 2.0, headlight_l)
        cmds.move(0.7, headlight_y, 2.0, headlight_r)
        
        components.append(headlight_l)
        components.append(headlight_r)
        cmds.parent(headlight_l, model_group)
        cmds.parent(headlight_r, model_group)
        
        # Apply materials
        for comp in components:
            cmds.sets(comp, forceElement=cmds.sets(name=f"{mat_name}SG", renderable=True, noSurfaceShader=True))
        
    elif model_type.lower() == "tree":
        # Get tree-specific parameters with defaults
        tree_type = parameters.get('type', 'oak')
        trunk_height = parameters.get('trunk_height', 5.0)
        trunk_radius = parameters.get('trunk_radius', 0.3)
        branches = parameters.get('branches', 5)
        leaf_density = parameters.get('leaf_density', 0.7)
        
        # Create trunk
        trunk = cmds.polyCylinder(r=trunk_radius, h=trunk_height, name=f"{name}_trunk")[0]
        cmds.move(0, trunk_height/2, 0, trunk)
        components.append(trunk)
        cmds.parent(trunk, model_group)
        
        # Create trunk material
        trunk_mat = cmds.shadingNode('lambert', asShader=True, name=f"{name}_trunk_material")
        cmds.setAttr(f"{trunk_mat}.color", 0.3, 0.2, 0.1, type='double3')
        cmds.sets(trunk, forceElement=cmds.sets(name=f"{trunk_mat}SG", renderable=True, noSurfaceShader=True))
        
        # Create foliage based on tree type
        if tree_type.lower() in ('oak', 'maple', 'deciduous'):
            # Create a spherical foliage for deciduous trees
            foliage_radius = trunk_height * 0.4 * leaf_density
            foliage = cmds.polySphere(r=foliage_radius, name=f"{name}_foliage")[0]
            cmds.move(0, trunk_height + foliage_radius * 0.5, 0, foliage)
            
            # Add some variation to make it less perfect
            cmds.select(foliage)
            cmds.polySmooth(divisions=1)
            
            components.append(foliage)
            cmds.parent(foliage, model_group)
            
        elif tree_type.lower() in ('pine', 'conifer', 'evergreen'):
            # Create a cone-shaped foliage for coniferous trees
            layers = int(3 + leaf_density * 2)
            max_radius = trunk_height * 0.3 * leaf_density
            layer_height = trunk_height * 0.2
            
            for i in range(layers):
                layer_radius = max_radius * (layers - i) / layers
                cone = cmds.polyCone(r=layer_radius, h=layer_height, name=f"{name}_foliage_{i}")[0]
                y_pos = trunk_height - (i * layer_height * 0.5) + (layers * layer_height * 0.5)
                cmds.move(0, y_pos, 0, cone)
                components.append(cone)
                cmds.parent(cone, model_group)
        
        elif tree_type.lower() in ('palm'):
            # Create a palm tree with a curved trunk and palm fronds
            # Curved trunk
            cmds.delete(trunk)  # Remove straight trunk
            segments = 8
            trunk = cmds.polyCylinder(r=trunk_radius, h=trunk_height/segments, subdivisionsHeight=1, name=f"{name}_trunk_base")[0]
            cmds.move(0, trunk_height/(segments*2), 0, trunk)
            components.append(trunk)
            
            # Create curved segments
            curve_direction = random.choice([-1, 1])  # Random curve direction
            for i in range(1, segments):
                segment = cmds.polyCylinder(r=trunk_radius * (1 - i * 0.05), h=trunk_height/segments, name=f"{name}_trunk_{i}")[0]
                y_pos = trunk_height * (i + 0.5) / segments
                x_offset = curve_direction * (math.sin(i / segments * math.pi * 0.5) * trunk_height * 0.15)
                cmds.move(x_offset, y_pos, 0, segment)
                # Rotate to follow curve
                angle = curve_direction * math.cos(i / segments * math.pi * 0.5) * 20
                cmds.rotate(0, 0, angle, segment)
                components.append(segment)
                cmds.parent(segment, model_group)
            
            # Create palm fronds as cones
            frond_count = int(6 + leaf_density * 4)
            for i in range(frond_count):
                angle = i * (360 / frond_count)
                frond = cmds.polyCone(r=0.1, h=2.0, subdivisionsHeight=1, name=f"{name}_frond_{i}")[0]
                cmds.move(0, trunk_height, 0, frond)
                cmds.rotate(60, angle, 0, frond)
                components.append(frond)
                cmds.parent(frond, model_group)
        
        # Create leaf material
        leaf_mat = cmds.shadingNode('lambert', asShader=True, name=f"{name}_leaf_material")
        leaf_color = [0.0, 0.5, 0.0]  # Default green
        
        # Adjust color based on tree type
        if tree_type.lower() in ('pine', 'conifer', 'evergreen'):
            leaf_color = [0.0, 0.3, 0.1]  # Darker green for pine
        elif tree_type.lower() in ('maple'):
            # Could be green, red, or orange for maple
            season = parameters.get('season', 'summer')
            if season == 'fall':
                leaf_color = [0.8, 0.3, 0.0]  # Orange/red for fall
        
        cmds.setAttr(f"{leaf_mat}.color", leaf_color[0], leaf_color[1], leaf_color[2], type='double3')
        
        # Apply leaf material to all foliage components except trunk
        foliage_components = [c for c in components if 'trunk' not in c]
        if foliage_components:
            cmds.sets(foliage_components, forceElement=cmds.sets(name=f"{leaf_mat}SG", renderable=True, noSurfaceShader=True))
        
    elif model_type.lower() == "building":
        # Get building parameters with defaults
        width = parameters.get('width', 10.0)
        height = parameters.get('height', 15.0)
        depth = parameters.get('depth', 10.0)
        floors = parameters.get('floors', 3)
        windows_per_floor = parameters.get('windows_per_floor', 4)
        
        # Create building base
        building = cmds.polyCube(w=width, h=height, d=depth, name=f"{name}_main")[0]
        cmds.move(0, height/2, 0, building)
        components.append(building)
        cmds.parent(building, model_group)
        
        # Create roof
        roof = cmds.polyCube(w=width*1.1, h=height*0.1, d=depth*1.1, name=f"{name}_roof")[0]
        cmds.move(0, height + height*0.05, 0, roof)
        components.append(roof)
        cmds.parent(roof, model_group)
        
        # Create windows
        window_width = width * 0.15
        window_height = height * 0.1
        floor_height = height / floors
        
        # Calculate spacing
        front_window_spacing = width / (windows_per_floor + 1)
        side_window_spacing = depth / (windows_per_floor + 1)
        
        # Create windows on front side
        for floor in range(floors):
            for i in range(windows_per_floor):
                # Front windows
                window = cmds.polyCube(w=window_width, h=window_height, d=0.1, name=f"{name}_window_front_{floor}_{i}")[0]
                window_x = (i + 1) * front_window_spacing - width/2
                window_y = (floor + 0.5) * floor_height
                cmds.move(window_x, window_y, depth/2, window)
                components.append(window)
                cmds.parent(window, model_group)
                
                # Back windows
                window = cmds.polyCube(w=window_width, h=window_height, d=0.1, name=f"{name}_window_back_{floor}_{i}")[0]
                cmds.move(window_x, window_y, -depth/2, window)
                components.append(window)
                cmds.parent(window, model_group)
        
        # Create windows on sides
        for floor in range(floors):
            for i in range(windows_per_floor):
                # Left side windows
                window = cmds.polyCube(w=0.1, h=window_height, d=window_width, name=f"{name}_window_left_{floor}_{i}")[0]
                window_z = (i + 1) * side_window_spacing - depth/2
                window_y = (floor + 0.5) * floor_height
                cmds.move(-width/2, window_y, window_z, window)
                components.append(window)
                cmds.parent(window, model_group)
                
                # Right side windows
                window = cmds.polyCube(w=0.1, h=window_height, d=window_width, name=f"{name}_window_right_{floor}_{i}")[0]
                cmds.move(width/2, window_y, window_z, window)
                components.append(window)
                cmds.parent(window, model_group)
                
        # Create door
        door_width = width * 0.2
        door_height = height * 0.2
        door = cmds.polyCube(w=door_width, h=door_height, d=0.1, name=f"{name}_door")[0]
        cmds.move(0, door_height/2, depth/2, door)
        components.append(door)
        cmds.parent(door, model_group)
        
        # Apply materials
        building_mat = cmds.shadingNode('lambert', asShader=True, name=f"{name}_building_material")
        cmds.setAttr(f"{building_mat}.color", color[0], color[1], color[2], type='double3')
        cmds.sets([building, roof], forceElement=cmds.sets(name=f"{building_mat}SG", renderable=True, noSurfaceShader=True))
        
        # Window material
        window_mat = cmds.shadingNode('lambert', asShader=True, name=f"{name}_window_material")
        cmds.setAttr(f"{window_mat}.color", 0.3, 0.7, 0.9, type='double3')
        # Get all window objects
        window_objects = [c for c in components if 'window' in c]
        if window_objects:
            cmds.sets(window_objects, forceElement=cmds.sets(name=f"{window_mat}SG", renderable=True, noSurfaceShader=True))
        
        # Door material
        door_mat = cmds.shadingNode('lambert', asShader=True, name=f"{name}_door_material")
        cmds.setAttr(f"{door_mat}.color", 0.4, 0.2, 0.1, type='double3')
        cmds.sets(door, forceElement=cmds.sets(name=f"{door_mat}SG", renderable=True, noSurfaceShader=True))
    
    elif model_type.lower() == "cup":
        # Get cup parameters
        radius = parameters.get('radius', 1.0)
        height = parameters.get('height', 2.0)
        handle = parameters.get('handle', True)
        
        # Create cup body
        cup = cmds.polyCylinder(r=radius, h=height, name=f"{name}_body")[0]
        cmds.move(0, height/2, 0, cup)
        
        # Create a hole in the cylinder to make it a cup
        inner_radius = radius * 0.8
        inner_height = height * 0.9
        inner = cmds.polyCylinder(r=inner_radius, h=inner_height, name=f"{name}_inner")[0]
        cmds.move(0, height/2 + (height - inner_height)/2, 0, inner)
        
        # Boolean the inner cylinder from the outer
        cup_final = cmds.polyCBoolOp(cup, inner, op=2, name=f"{name}_cup")[0]
        components.append(cup_final)
        cmds.parent(cup_final, model_group)
        
        # Create handle if requested
        if handle:
            # Create a curved handle using a torus
            handle = cmds.polyTorus(r=radius*0.8, sr=radius*0.1, twist=90, name=f"{name}_handle")[0]
            # Cut the torus to create a C-shaped handle
            cmds.select(f"{handle}.f[0:10]")  # Select some faces to delete
            cmds.delete()
            # Position the handle
            cmds.move(radius, height/2, 0, handle)
            cmds.rotate(0, 90, 0, handle)
            components.append(handle)
            cmds.parent(handle, model_group)
            
            # Create a unified material
            cmds.sets([cup_final, handle], forceElement=cmds.sets(name=f"{mat_name}SG", renderable=True, noSurfaceShader=True))
        else:
            # Apply material just to the cup
            cmds.sets(cup_final, forceElement=cmds.sets(name=f"{mat_name}SG", renderable=True, noSurfaceShader=True))
    
    elif model_type.lower() == "chair":
        # Get chair parameters
        seat_width = parameters.get('seat_width', 2.0)
        seat_depth = parameters.get('seat_depth', 2.0)
        seat_height = parameters.get('seat_height', 1.5)
        back_height = parameters.get('back_height', 3.0)
        
        # Create seat
        seat = cmds.polyCube(w=seat_width, h=0.2, d=seat_depth, name=f"{name}_seat")[0]
        cmds.move(0, seat_height, 0, seat)
        components.append(seat)
        cmds.parent(seat, model_group)
        
        # Create back
        back = cmds.polyCube(w=seat_width, h=back_height, d=0.2, name=f"{name}_back")[0]
        cmds.move(0, seat_height + back_height/2, -seat_depth/2, back)
        components.append(back)
        cmds.parent(back, model_group)
        
        # Create legs
        leg_positions = [
            [seat_width/2 - 0.1, seat_height/2, seat_depth/2 - 0.1],    # Front right
            [-seat_width/2 + 0.1, seat_height/2, seat_depth/2 - 0.1],   # Front left
            [seat_width/2 - 0.1, seat_height/2, -seat_depth/2 + 0.1],   # Back right
            [-seat_width/2 + 0.1, seat_height/2, -seat_depth/2 + 0.1]   # Back left
        ]
        
        for i, pos in enumerate(leg_positions):
            leg = cmds.polyCube(w=0.2, h=seat_height, d=0.2, name=f"{name}_leg_{i}")[0]
            cmds.move(pos[0], pos[1], pos[2], leg)
            components.append(leg)
            cmds.parent(leg, model_group)
        
        # Apply materials
        cmds.sets(components, forceElement=cmds.sets(name=f"{mat_name}SG", renderable=True, noSurfaceShader=True))
        
    else:
        raise ValueError(f"Error: unknown model type {model_type}, use one of these types: car, tree, building, cup, chair")
    
    return finalize_model()