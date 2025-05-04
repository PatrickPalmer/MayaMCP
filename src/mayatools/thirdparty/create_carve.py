from typing import Dict, List, Any, Optional, Union, Tuple


def create_curve(
    curve_type: str,
    name: str = None,
    points: List[List[float]] = None,
    parameters: Dict[str, Any] = None,
    translate: List[float] = [0.0, 0.0, 0.0],
    rotate: List[float] = [0.0, 0.0, 0.0],
    scale: List[float] = [1.0, 1.0, 1.0]
) -> Dict[str, Any]:
    """Creates a curve in the Maya scene.
    
    Available curve types:
    - custom: Create a curve from specified points
    - line: Create a straight line
    - circle: Create a circular curve
    - square: Create a square curve
    - rectangle: Create a rectangular curve
    - spiral: Create a spiral curve
    - helix: Create a helix curve
    - arc: Create an arc curve
    - star: Create a star-shaped curve
    - gear: Create a gear-shaped curve
    
    Points is a list of 3D points that define the curve vertices.
    For custom curves, points must be provided.
    For other curve types, points is optional and will override default shapes.
    
    Parameters is a dictionary containing curve-specific settings.
    Example parameters for circle: {'radius': 5.0}
    Example parameters for spiral: {'radius': 5.0, 'height': 2.0, 'turns': 3}
    
    Translate, rotate and scale are applied to the final curve.
    """
    import maya.cmds as cmds
    import random
    import math
    
    def _validate_vector3d(vec:List[float]):
        return isinstance(vec, list) and len(vec) == 3 and all([isinstance(v, float) for v in vec])
    
    # Validate inputs
    if curve_type.lower() == "custom" and not points:
        raise ValueError("Points must be provided for custom curve type")
    
    if points and not all([_validate_vector3d(p) for p in points]):
        raise ValueError("Invalid point format. Each point must be a list of 3 float values.")
    
    if not _validate_vector3d(translate):
        raise ValueError("Invalid translate format. Must be a list of 3 float values.")
    
    if not _validate_vector3d(rotate):
        raise ValueError("Invalid rotate format. Must be a list of 3 float values.")
    
    if not _validate_vector3d(scale):
        raise ValueError("Invalid scale format. Must be a list of 3 float values.")
    
    # Set default parameters dict if none provided
    if parameters is None:
        parameters = {}
    
    # Set default name if none provided
    if name is None:
        name = f"{curve_type}_curve_{int(random.random() * 1000)}"
    
    # Generate curve points based on type
    if curve_type.lower() == "custom":
        # Use the provided points directly
        curve_points = points
    
    elif curve_type.lower() == "line":
        # Create a straight line
        start_point = parameters.get('start_point', [-5.0, 0.0, 0.0])
        end_point = parameters.get('end_point', [5.0, 0.0, 0.0])
        
        if points and len(points) >= 2:
            start_point = points[0]
            end_point = points[-1]
        
        curve_points = [start_point, end_point]
    
    elif curve_type.lower() == "circle":
        # Create a circle
        radius = parameters.get('radius', 5.0)
        segments = parameters.get('segments', 8)
        
        curve_points = []
        for i in range(segments):
            angle = 2.0 * math.pi * i / segments
            x = radius * math.cos(angle)
            z = radius * math.sin(angle)
            curve_points.append([x, 0.0, z])
        
        # Close the circle by adding the first point again
        curve_points.append(curve_points[0])
    
    elif curve_type.lower() == "square":
        # Create a square
        size = parameters.get('size', 5.0)
        half_size = size / 2.0
        
        curve_points = [
            [-half_size, 0.0, -half_size],
            [half_size, 0.0, -half_size],
            [half_size, 0.0, half_size],
            [-half_size, 0.0, half_size],
            [-half_size, 0.0, -half_size]  # Close the square
        ]
    
    elif curve_type.lower() == "rectangle":
        # Create a rectangle
        width = parameters.get('width', 8.0)
        depth = parameters.get('depth', 5.0)
        half_width = width / 2.0
        half_depth = depth / 2.0
        
        curve_points = [
            [-half_width, 0.0, -half_depth],
            [half_width, 0.0, -half_depth],
            [half_width, 0.0, half_depth],
            [-half_width, 0.0, half_depth],
            [-half_width, 0.0, -half_depth]  # Close the rectangle
        ]
    
    elif curve_type.lower() == "spiral":
        # Create a spiral
        radius = parameters.get('radius', 5.0)
        height = parameters.get('height', 2.0)
        turns = parameters.get('turns', 3)
        segments = parameters.get('segments', 32 * turns)
        
        curve_points = []
        for i in range(segments + 1):
            angle = 2.0 * math.pi * turns * i / segments
            r = radius * (i / segments)
            x = r * math.cos(angle)
            z = r * math.sin(angle)
            y = height * (i / segments)
            curve_points.append([x, y, z])
    
    elif curve_type.lower() == "helix":
        # Create a helix
        radius = parameters.get('radius', 5.0)
        height = parameters.get('height', 10.0)
        turns = parameters.get('turns', 3)
        segments = parameters.get('segments', 32 * turns)
        
        curve_points = []
        for i in range(segments + 1):
            angle = 2.0 * math.pi * turns * i / segments
            x = radius * math.cos(angle)
            z = radius * math.sin(angle)
            y = height * (i / segments)
            curve_points.append([x, y, z])
    
    elif curve_type.lower() == "arc":
        # Create an arc
        radius = parameters.get('radius', 5.0)
        start_angle = parameters.get('start_angle', 0.0)
        end_angle = parameters.get('end_angle', 180.0)
        segments = parameters.get('segments', 16)
        
        # Convert angles to radians
        start_rad = math.radians(start_angle)
        end_rad = math.radians(end_angle)
        
        curve_points = []
        for i in range(segments + 1):
            t = i / segments
            angle = start_rad + t * (end_rad - start_rad)
            x = radius * math.cos(angle)
            z = radius * math.sin(angle)
            curve_points.append([x, 0.0, z])
    
    elif curve_type.lower() == "star":
        # Create a star
        outer_radius = parameters.get('outer_radius', 5.0)
        inner_radius = parameters.get('inner_radius', 2.5)
        points_count = parameters.get('points_count', 5)
        
        curve_points = []
        for i in range(points_count * 2):
            angle = math.pi * i / points_count
            radius = outer_radius if i % 2 == 0 else inner_radius
            x = radius * math.cos(angle)
            z = radius * math.sin(angle)
            curve_points.append([x, 0.0, z])
        
        # Close the star
        curve_points.append(curve_points[0])
    
    elif curve_type.lower() == "gear":
        # Create a gear
        radius = parameters.get('radius', 5.0)
        tooth_height = parameters.get('tooth_height', 1.0)
        tooth_count = parameters.get('tooth_count', 12)
        
        curve_points = []
        for i in range(tooth_count * 2):
            angle = 2.0 * math.pi * i / (tooth_count * 2)
            r = radius if i % 2 == 0 else radius + tooth_height
            x = r * math.cos(angle)
            z = r * math.sin(angle)
            curve_points.append([x, 0.0, z])
        
        # Close the gear
        curve_points.append(curve_points[0])
    
    else:
        raise ValueError(f"Unknown curve type: {curve_type}. Use custom, line, circle, square, rectangle, spiral, helix, arc, star, or gear")
    
    # Create the curve
    degree = parameters.get('degree', 1)  # Linear by default, 3 for smooth curve
    
    if parameters.get('periodic', False) and len(curve_points) > 3:
        # Create a periodic (closed) curve
        curve = cmds.curve(name=name, p=curve_points, degree=degree, periodic=True)
    else:
        # Create a standard curve
        curve = cmds.curve(name=name, p=curve_points, degree=min(degree, len(curve_points)-1))
    
    # Apply transformations
    cmds.setAttr(f"{curve}.translate", translate[0], translate[1], translate[2], type="double3")
    cmds.setAttr(f"{curve}.rotate", rotate[0], rotate[1], rotate[2], type="double3")
    cmds.setAttr(f"{curve}.scale", scale[0], scale[1], scale[2], type="double3")
    
    return {
        "success": True,
        "name": curve,
        "curve_type": curve_type,
        "points_count": len(curve_points),
        "translate": translate,
        "rotate": rotate,
        "scale": scale
    }