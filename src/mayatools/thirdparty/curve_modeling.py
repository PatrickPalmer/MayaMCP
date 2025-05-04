from typing import Dict, List, Any, Optional, Union


def curve_modeling(
    operation: str,
    curves: List[str],
    name: str = None,
    parameters: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Create geometry from curves using various modeling techniques.
    
    Available operations:
    - extrude: Extrude a profile curve along a path curve
    - loft: Create a surface that passes through multiple profile curves
    - revolve: Revolve a profile curve around an axis
    - sweep: Sweep a profile curve along a path curve
    - planar: Create a planar surface from a closed curve
    - bevel: Create a beveled surface along a curve
    
    curves: List of curve names to use in the operation
    For extrude: [profile_curve, path_curve]
    For loft: [curve1, curve2, curve3, ...]
    For revolve: [profile_curve]
    For sweep: [profile_curve, path_curve]
    For planar: [closed_curve]
    For bevel: [path_curve]
    
    Parameters: Dictionary of operation-specific parameters
    Example for extrude: {'scale': 1.0, 'twist': 0.0}
    Example for revolve: {'axis': 'y', 'angle': 360.0, 'sections': 8}
    """
    import maya.cmds as cmds
    import random
    
    # Validate input curves
    for curve in curves:
        if not cmds.objExists(curve):
            raise ValueError(f"Curve {curve} does not exist")
        
        if cmds.objectType(curve) != 'transform':
            # Check if it's a direct nurbs curve shape
            shape_type = cmds.objectType(curve)
            if shape_type != 'nurbsCurve':
                shape_nodes = cmds.listRelatives(curve, shapes=True)
                if not shape_nodes or cmds.objectType(shape_nodes[0]) != 'nurbsCurve':
                    raise ValueError(f"{curve} is not a NURBS curve")
    
    # Set default parameters dict if none provided
    if parameters is None:
        parameters = {}
    
    # Set default name if none provided
    if name is None:
        name = f"{operation}_{int(random.random() * 1000)}"
    
    # Perform the requested operation
    if operation.lower() == "extrude":
        if len(curves) < 2:
            raise ValueError("Extrude operation requires at least two curves: profile and path")
        
        profile_curve = curves[0]
        path_curve = curves[1]
        
        # Get extrude parameters
        scale = parameters.get('scale', 1.0)
        twist = parameters.get('twist', 0.0)
        taper = parameters.get('taper', 1.0)
        
        # Create the extrusion
        extrude = cmds.extrude(
            profile_curve, 
            path_curve, 
            name=name,
            scale=scale,
            twist=twist,
            taper=taper,
            useComponentPivot=1,
            fixedPath=True
        )
        
        return {
            "success": True,
            "name": extrude[0],
            "operation": "extrude",
            "profile_curve": profile_curve,
            "path_curve": path_curve
        }
    
    elif operation.lower() == "loft":
        if len(curves) < 2:
            raise ValueError("Loft operation requires at least two curves")
        
        # Get loft parameters
        degree = parameters.get('degree', 3)
        sections = parameters.get('sections', 1)
        uniform = parameters.get('uniform', True)
        close = parameters.get('close', False)
        
        # Create the loft surface
        loft = cmds.loft(
            *curves,
            name=name,
            degree=degree,
            sectionSpans=sections,
            uniform=uniform,
            close=close,
            autoReverse=True
        )
        
        return {
            "success": True,
            "name": loft[0],
            "operation": "loft",
            "curves": curves
        }
    
    elif operation.lower() == "revolve":
        if len(curves) < 1:
            raise ValueError("Revolve operation requires at least one profile curve")
        
        profile_curve = curves[0]
        
        # Get revolve parameters
        axis = parameters.get('axis', 'y').lower()
        angle = parameters.get('angle', 360.0)
        sections = parameters.get('sections', 8)
        
        # Map axis to pivot and axis vectors
        pivot = [0, 0, 0]
        axis_vector = [0, 1, 0]  # Default Y axis
        
        if axis == 'x':
            axis_vector = [1, 0, 0]
        elif axis == 'z':
            axis_vector = [0, 0, 1]
        
        # Create the revolved surface
        revolve = cmds.revolve(
            profile_curve,
            name=name,
            pivot=pivot,
            axis=axis_vector,
            degree=3,
            sections=sections,
            sweepType=1,  # 0=linear, 1=circular, 2=square
            useTolerance=True,
            startSweep=0,
            endSweep=angle
        )
        
        return {
            "success": True,
            "name": revolve[0],
            "operation": "revolve",
            "profile_curve": profile_curve,
            "axis": axis,
            "angle": angle
        }
    
    elif operation.lower() == "sweep":
        if len(curves) < 2:
            raise ValueError("Sweep operation requires at least two curves: profile and path")
        
        profile_curve = curves[0]
        path_curve = curves[1]
        
        # Get sweep parameters
        scale = parameters.get('scale', 1.0)
        twist = parameters.get('twist', 0.0)
        orientation = parameters.get('orientation', 0)
        
        # Create the sweep
        sweep = cmds.sweep(
            profile_curve,
            path_curve,
            name=name,
            scale=scale,
            rotation=twist,
            useComponentPivot=1,
            orientationMode=orientation  # 0=tangent, 1=component, 2=surface
        )
        
        return {
            "success": True,
            "name": sweep[0],
            "operation": "sweep",
            "profile_curve": profile_curve,
            "path_curve": path_curve
        }
    
    elif operation.lower() == "planar":
        if len(curves) < 1:
            raise ValueError("Planar operation requires at least one closed curve")
        
        # Check if the curve is closed
        profile_curve = curves[0]
        curve_info = cmds.ls(profile_curve, dag=True)
        
        # Create the planar surface
        try:
            planar = cmds.planarSrf(
                profile_curve,
                name=name,
                degree=3
            )
            
            return {
                "success": True,
                "name": planar[0],
                "operation": "planar",
                "profile_curve": profile_curve
            }
        except Exception as e:
            # If the planar surface creation fails, try to create a mesh instead
            try:
                # Convert curve to polygons
                mesh = cmds.nurbsToPoly(
                    profile_curve,
                    name=name,
                    constructionHistory=False
                )
                
                return {
                    "success": True,
                    "name": mesh[0],
                    "operation": "planar_mesh",
                    "profile_curve": profile_curve,
                    "note": "Created polygon mesh instead of NURBS surface"
                }
            except:
                raise ValueError(f"Failed to create planar surface from {profile_curve}. The curve may not be closed or planar.")
    
    elif operation.lower() == "bevel":
        if len(curves) < 1:
            raise ValueError("Bevel operation requires at least one path curve")
        
        path_curve = curves[0]
        
        # Get bevel parameters
        width = parameters.get('width', 0.5)
        depth = parameters.get('depth', 0.5)
        segments = parameters.get('segments', 4)
        
        # Create circle profile for the bevel
        profile_name = f"temp_bevel_profile_{int(random.random() * 1000)}"
        profile = cmds.circle(name=profile_name, radius=width, sections=segments, normal=[0, 1, 0])[0]
        
        # Use extrude to create the beveled shape
        bevel = cmds.extrude(
            profile,
            path_curve,
            name=name,
            fixedPath=True
        )
        
        # Delete the temporary profile
        cmds.delete(profile)
        
        return {
            "success": True,
            "name": bevel[0],
            "operation": "bevel",
            "path_curve": path_curve
        }
    
    else:
        raise ValueError(f"Unknown operation: {operation}. Use extrude, loft, revolve, sweep, planar, or bevel")