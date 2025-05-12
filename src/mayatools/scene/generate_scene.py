from typing import Dict, List, Any, Optional, Union


def generate_scene(
    scene_type: str,
    name: str = None,
    parameters: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Generate a complete 3D scene with multiple objects arranged according to a theme.
    
    Available scene types:
    - city: Generate a city with buildings, streets, and cars
    - forest: Generate a forest with trees, terrain, and optional paths
    - living_room: Generate a living room with furniture and decorations
    - office: Generate an office with desks, chairs, and office equipment
    - park: Generate a park with trees, benches, and paths
    
    Parameters is a dictionary containing scene-specific settings.
    Example for city: {'blocks': 3, 'building_density': 0.8, 'include_cars': True}
    Example for forest: {'tree_count': 15, 'forest_size': 50.0, 'include_path': True}
    
    Returns a dictionary with information about the created scene and objects.
    """
    import maya.cmds as cmds
    import random
    import math
    
    # Set default parameters dict if none provided
    if parameters is None:
        parameters = {}
    
    # Set default name if none provided
    if name is None:
        name = f"{scene_type}_scene_{int(random.random() * 1000)}"
    
    # Create a root group for the entire scene
    scene_group = cmds.group(empty=True, name=name)
    created_objects = []
    
    # Import required Maya tools for advanced model creation
    import sys
    import os
    
    # Find the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Navigate up to the mayatools directory
    mayatools_dir = os.path.dirname(script_dir)
    
    # Add to sys.path if not already there
    if mayatools_dir not in sys.path:
        sys.path.append(mayatools_dir)
    
    # Import the relevant tools
    from thirdparty.create_advanced_model import create_advanced_model
    from thirdparty.create_material import create_material
    from thirdparty.organize_objects import organize_objects
    
    def _create_and_track(func, **kwargs):
        """Helper to call a function and track its created objects"""
        result = func(**kwargs)
        if "name" in result:
            created_objects.append(cabinet)
            cmds.parent(cabinet, scene_group)
            
            # Create cabinet material
            cabinet_color = [0.8, 0.8, 0.8] if modern_style else [0.6, 0.4, 0.2]
            _create_and_track(
                create_material,
                material_type="lambert" if modern_style else "wood",
                name=f"{name}_cabinet_{i}_material",
                color=cabinet_color,
                assign_to=cabinet
            )
        
        return {
            "success": True,
            "name": scene_group,
            "scene_type": "office",
            "objects_count": len(created_objects),
            "desks_count": desk_count
        }
    
    elif scene_type.lower() == "park":
        # Get park parameters
        park_size = parameters.get('park_size', 60.0)
        tree_count = parameters.get('tree_count', 10)
        include_benches = parameters.get('include_benches', True)
        include_fountain = parameters.get('include_fountain', True)
        
        # Create ground
        ground = cmds.polyPlane(
            name=f"{name}_ground",
            width=park_size,
            height=park_size,
            subdivisionsX=20,
            subdivisionsY=20
        )[0]
        created_objects.append(ground)
        cmds.parent(ground, scene_group)
        
        # Apply slight noise to terrain for natural look
        cmds.select(f"{ground}.vtx[*]")
        vertices = cmds.ls(selection=True, flatten=True)
        for vertex in vertices:
            if random.random() < 0.6:  # Don't displace every vertex
                height = random.uniform(0, 0.2)
                cmds.move(0, height, 0, vertex, relative=True)
        
        # Create grass material
        _create_and_track(
            create_material,
            material_type="lambert",
            name=f"{name}_grass_material",
            color=[0.2, 0.6, 0.2],  # Green
            assign_to=ground
        )
        
        # Create central circular path
        path_radius = park_size * 0.3
        
        # Create path circle curve
        path_points = []
        path_segments = 24
        
        for i in range(path_segments + 1):
            angle = 2.0 * math.pi * i / path_segments
            x = path_radius * math.cos(angle)
            z = path_radius * math.sin(angle)
            path_points.append([x, 0.1, z])  # Slightly above ground
        
        # Create the path as a nurbs curve
        path_curve = cmds.curve(
            name=f"{name}_path_curve",
            p=path_points,
            degree=3,
            periodic=True
        )
        
        # Create a profile for the path
        path_profile = cmds.circle(
            name=f"{name}_path_profile",
            radius=1.5,
            normal=[0, 1, 0]
        )[0]
        
        # Extrude the profile along the curve
        path = cmds.extrude(
            path_profile,
            path_curve,
            name=f"{name}_path",
            fixedPath=True
        )[0]
        
        # Create path material
        _create_and_track(
            create_material,
            material_type="lambert",
            name=f"{name}_path_material",
            color=[0.8, 0.8, 0.7],  # Light tan
            assign_to=path
        )
        
        created_objects.append(path)
        cmds.parent(path, scene_group)
        
        # Clean up temporary curve and profile
        cmds.delete(path_curve, path_profile)
        
        # Add trees around the park
        tree_types = ["oak", "pine", "maple"]
        
        for t in range(tree_count):
            # Place trees with some randomness, but avoiding the path
            distance = random.uniform(path_radius + 5, park_size/2 * 0.9)
            angle = random.uniform(0, 2 * math.pi)
            
            tree_x = distance * math.cos(angle)
            tree_z = distance * math.sin(angle)
            
            # Get approximate ground height at this position
            ground_height = 0
            
            # Randomize tree parameters
            tree_type = random.choice(tree_types)
            tree_scale = random.uniform(0.8, 1.5)
            
            # Create the tree
            tree = _create_and_track(
                create_advanced_model,
                model_type="tree",
                name=f"{name}_tree_{t}",
                translate=[tree_x, ground_height, tree_z],
                rotate=[0, random.uniform(0, 360), 0],
                scale=tree_scale,
                parameters={
                    'type': tree_type,
                    'trunk_height': random.uniform(4.0, 7.0),
                    'branches': int(random.uniform(3, 6)),
                    'leaf_density': random.uniform(0.6, 0.9)
                }
            )
        
        # Add benches around the path
        if include_benches:
            bench_count = int(path_radius / 5)  # Roughly one bench every 5 units
            
            for b in range(bench_count):
                angle = 2.0 * math.pi * b / bench_count
                
                # Place benches slightly outside the path
                bench_radius = path_radius + 3.0
                bench_x = bench_radius * math.cos(angle)
                bench_z = bench_radius * math.sin(angle)
                
                # Create bench seat
                bench_seat = cmds.polyCube(
                    name=f"{name}_bench_seat_{b}",
                    width=3.0,
                    height=0.2,
                    depth=1.0
                )[0]
                
                # Create bench back
                bench_back = cmds.polyCube(
                    name=f"{name}_bench_back_{b}",
                    width=3.0,
                    height=1.0,
                    depth=0.2
                )[0]
                
                # Position and orient the bench to face the center
                cmds.move(bench_x, 0.6, bench_z, bench_seat)
                cmds.move(bench_x, 1.2, bench_z - 0.4, bench_back)
                
                # Rotate to face center
                bench_rot_y = math.degrees(angle) + 180
                cmds.rotate(0, bench_rot_y, 0, bench_seat)
                cmds.rotate(0, bench_rot_y, 0, bench_back)
                
                created_objects.extend([bench_seat, bench_back])
                cmds.parent([bench_seat, bench_back], scene_group)
                
                # Create bench material
                _create_and_track(
                    create_material,
                    material_type="wood",
                    name=f"{name}_bench_material_{b}",
                    color=[0.6, 0.4, 0.2],  # Brown
                    assign_to=[bench_seat, bench_back]
                )
        
        # Add central fountain
        if include_fountain:
            # Create fountain base
            fountain_radius = 5.0
            fountain_base = cmds.polyCylinder(
                name=f"{name}_fountain_base",
                radius=fountain_radius,
                height=1.0
            )[0]
            cmds.move(0, 0.5, 0, fountain_base)
            
            # Create water pool
            water_pool = cmds.polyCylinder(
                name=f"{name}_water_pool",
                radius=fountain_radius * 0.9,
                height=0.8
            )[0]
            cmds.move(0, 0.5, 0, water_pool)
            
            # Create central column
            fountain_column = cmds.polyCylinder(
                name=f"{name}_fountain_column",
                radius=fountain_radius * 0.2,
                height=3.0
            )[0]
            cmds.move(0, 1.5, 0, fountain_column)
            
            # Create top bowl
            top_bowl = cmds.polyCylinder(
                name=f"{name}_top_bowl",
                radius=fountain_radius * 0.5,
                height=0.5
            )[0]
            cmds.move(0, 3.0, 0, top_bowl)
            
            created_objects.extend([fountain_base, water_pool, fountain_column, top_bowl])
            cmds.parent([fountain_base, water_pool, fountain_column, top_bowl], scene_group)
            
            # Create materials
            _create_and_track(
                create_material,
                material_type="stone",
                name=f"{name}_fountain_material",
                color=[0.7, 0.7, 0.7],  # Gray stone
                assign_to=[fountain_base, fountain_column, top_bowl]
            )
            
            _create_and_track(
                create_material,
                material_type="glass",
                name=f"{name}_water_material",
                color=[0.2, 0.4, 0.8],  # Blue water
                assign_to=water_pool
            )
        
        return {
            "success": True,
            "name": scene_group,
            "scene_type": "park",
            "objects_count": len(created_objects),
            "trees_count": tree_count,
            "has_benches": include_benches,
            "has_fountain": include_fountain
        }
    
    else:
        raise ValueError(f"Unknown scene type: {scene_type}. Use city, forest, living_room, office, or park")
.append(result["name"])
            # Parent to scene group
            try:
                cmds.parent(result["name"], scene_group)
            except:
                # May already be parented if the function does grouping internally
                pass
        return result
    
    # Generate scene based on type
    if scene_type.lower() == "city":
        # Get city parameters
        blocks = parameters.get('blocks', 3)
        building_density = parameters.get('building_density', 0.8)
        include_cars = parameters.get('include_cars', True)
        street_width = parameters.get('street_width', 10.0)
        block_size = parameters.get('block_size', 30.0)
        
        # Create ground plane
        city_size = blocks * (block_size + street_width)
        ground = cmds.polyPlane(name=f"{name}_ground", width=city_size, height=city_size, subdivisionsX=blocks*2, subdivisionsY=blocks*2)[0]
        created_objects.append(ground)
        cmds.parent(ground, scene_group)
        
        # Create buildings for each block
        building_count = 0
        for block_x in range(blocks):
            for block_z in range(blocks):
                # Calculate block position
                block_center_x = (block_x - blocks/2 + 0.5) * (block_size + street_width)
                block_center_z = (block_z - blocks/2 + 0.5) * (block_size + street_width)
                
                # Determine number of buildings for this block
                buildings_per_block = int(random.uniform(1, 4))
                
                for b in range(buildings_per_block):
                    # Skip some buildings based on density
                    if random.random() > building_density:
                        continue
                    
                    # Calculate building position within block
                    offset_x = random.uniform(-block_size/3, block_size/3)
                    offset_z = random.uniform(-block_size/3, block_size/3)
                    building_x = block_center_x + offset_x
                    building_z = block_center_z + offset_z
                    
                    # Randomize building parameters
                    building_height = random.uniform(10.0, 50.0)
                    building_width = random.uniform(5.0, 15.0)
                    building_depth = random.uniform(5.0, 15.0)
                    
                    # Create the building
                    building = _create_and_track(
                        create_advanced_model,
                        model_type="building",
                        name=f"{name}_building_{building_count}",
                        translate=[building_x, 0, building_z],
                        parameters={
                            'height': building_height,
                            'width': building_width, 
                            'depth': building_depth,
                            'floors': int(building_height / 4),
                            'windows_per_floor': int(max(building_width, building_depth) / 2)
                        }
                    )
                    
                    building_count += 1
        
        # Add cars if requested
        if include_cars:
            car_count = int(blocks * blocks * 0.5)  # Fewer cars than buildings
            
            for c in range(car_count):
                # Place cars on the street grid
                street_x = random.randint(0, blocks) * (block_size + street_width) - city_size/2
                street_z = random.randint(0, blocks) * (block_size + street_width) - city_size/2
                
                # Small random offset to avoid perfect alignment
                street_x += random.uniform(-2.0, 2.0)
                street_z += random.uniform(-2.0, 2.0)
                
                # Randomize car parameters
                car_type = random.choice(["sporty", "standard"])
                car_color = [random.random(), random.random(), random.random()]
                
                # Create the car
                car = _create_and_track(
                    create_advanced_model,
                    model_type="car",
                    name=f"{name}_car_{c}",
                    translate=[street_x, 0, street_z],
                    rotate=[0, random.uniform(0, 360), 0],
                    color=car_color,
                    scale=random.uniform(0.8, 1.2),
                    parameters={
                        'sporty': car_type == "sporty",
                        'convertible': random.random() > 0.7
                    }
                )
        
        return {
            "success": True,
            "name": scene_group,
            "scene_type": "city",
            "objects_count": len(created_objects),
            "buildings_count": building_count,
            "cars_count": car_count if include_cars else 0
        }
    
    elif scene_type.lower() == "forest":
        # Get forest parameters
        tree_count = parameters.get('tree_count', 15)
        forest_size = parameters.get('forest_size', 50.0)
        include_path = parameters.get('include_path', True)
        terrain_roughness = parameters.get('terrain_roughness', 0.3)
        
        # Create ground/terrain
        ground = cmds.polyPlane(
            name=f"{name}_ground", 
            width=forest_size, 
            height=forest_size, 
            subdivisionsX=20, 
            subdivisionsY=20
        )[0]
        created_objects.append(ground)
        cmds.parent(ground, scene_group)
        
        # Apply some random noise to the terrain
        if terrain_roughness > 0:
            # Select all vertices
            cmds.select(f"{ground}.vtx[*]")
            
            # Apply random displacement
            vertices = cmds.ls(selection=True, flatten=True)
            for vertex in vertices:
                if random.random() < 0.7:  # Don't displace every vertex
                    height = random.uniform(0, terrain_roughness * 5) 
                    cmds.move(0, height, 0, vertex, relative=True)
        
        # Create a nice terrain material
        _create_and_track(
            create_material,
            material_type="lambert",
            name=f"{name}_ground_material",
            color=[0.3, 0.5, 0.2],  # Green-brown
            assign_to=ground
        )
        
        # Add trees
        tree_types = ["oak", "pine", "maple"]
        for t in range(tree_count):
            # Randomize tree position within forest
            tree_x = random.uniform(-forest_size/2 * 0.9, forest_size/2 * 0.9)
            tree_z = random.uniform(-forest_size/2 * 0.9, forest_size/2 * 0.9)
            
            # Get ground height at this position (approximate)
            # This is a simple approximation - in a real tool, we'd do a proper raycast
            ground_height = 0
            if terrain_roughness > 0:
                ground_height = random.uniform(0, terrain_roughness * 3)
            
            # Randomize tree parameters
            tree_type = random.choice(tree_types)
            tree_scale = random.uniform(0.8, 1.5)
            trunk_height = random.uniform(4.0, 8.0)
            
            # Create the tree
            tree = _create_and_track(
                create_advanced_model,
                model_type="tree",
                name=f"{name}_tree_{t}",
                translate=[tree_x, ground_height, tree_z],
                rotate=[0, random.uniform(0, 360), 0],
                scale=tree_scale,
                parameters={
                    'type': tree_type,
                    'trunk_height': trunk_height,
                    'branches': int(random.uniform(3, 7)),
                    'leaf_density': random.uniform(0.6, 0.9)
                }
            )
        
        # Add a path if requested
        if include_path:
            # Create a simple curved path through the forest
            path_points = []
            path_segments = 10
            
            # Generate a meandering path from one side to the other
            for i in range(path_segments + 1):
                t = i / path_segments
                x = (t - 0.5) * forest_size
                z = math.sin(t * math.pi * 2) * forest_size * 0.3
                path_points.append([x, 0.1, z])  # Slightly above ground
            
            # Create the path as a nurbs curve
            path_curve = cmds.curve(
                name=f"{name}_path_curve",
                p=path_points,
                degree=3
            )
            
            # Extrude a circle along the path to create a 3D path
            path_profile = cmds.circle(
                name=f"{name}_path_profile",
                radius=1.0,
                normal=[0, 1, 0]
            )[0]
            
            path = cmds.extrude(
                path_profile,
                path_curve,
                name=f"{name}_path",
                fixedPath=True
            )[0]
            
            # Create path material
            _create_and_track(
                create_material,
                material_type="lambert",
                name=f"{name}_path_material",
                color=[0.7, 0.6, 0.5],  # Tan/brown
                assign_to=path
            )
            
            created_objects.append(path)
            cmds.parent(path, scene_group)
            
            # Clean up temporary curve and profile
            cmds.delete(path_curve, path_profile)
        
        return {
            "success": True,
            "name": scene_group,
            "scene_type": "forest",
            "objects_count": len(created_objects),
            "trees_count": tree_count,
            "has_path": include_path
        }
    
    elif scene_type.lower() == "living_room":
        # Get living room parameters
        room_size = parameters.get('room_size', 25.0)
        furniture_density = parameters.get('furniture_density', 1.0)
        modern_style = parameters.get('modern_style', True)
        
        # Create room (floor, walls, ceiling)
        floor = cmds.polyPlane(name=f"{name}_floor", width=room_size, height=room_size)[0]
        created_objects.append(floor)
        cmds.parent(floor, scene_group)
        
        wall_height = 12.0
        
        # Create 4 walls
        for i, (pos, rot) in enumerate([
            ([0, wall_height/2, -room_size/2], [0, 0, 0]),      # Back wall
            ([0, wall_height/2, room_size/2], [0, 180, 0]),     # Front wall
            ([-room_size/2, wall_height/2, 0], [0, 90, 0]),     # Left wall
            ([room_size/2, wall_height/2, 0], [0, -90, 0])      # Right wall
        ]):
            wall = cmds.polyPlane(
                name=f"{name}_wall_{i}",
                width=room_size,
                height=wall_height
            )[0]
            cmds.move(pos[0], pos[1], pos[2], wall)
            cmds.rotate(rot[0], rot[1], rot[2], wall)
            created_objects.append(wall)
            cmds.parent(wall, scene_group)
        
        # Create ceiling
        ceiling = cmds.polyPlane(name=f"{name}_ceiling", width=room_size, height=room_size)[0]
        cmds.move(0, wall_height, 0, ceiling)
        cmds.rotate(180, 0, 0, ceiling)
        created_objects.append(ceiling)
        cmds.parent(ceiling, scene_group)
        
        # Create wall and floor materials
        _create_and_track(
            create_material,
            material_type="lambert",
            name=f"{name}_wall_material",
            color=[0.9, 0.9, 0.85],  # Off-white
            assign_to=[f"{name}_wall_0", f"{name}_wall_1", f"{name}_wall_2", f"{name}_wall_3", f"{name}_ceiling"]
        )
        
        _create_and_track(
            create_material,
            material_type="wood",
            name=f"{name}_floor_material",
            color=[0.7, 0.5, 0.3],  # Medium brown
            parameters={'veinSpread': 0.3},
            assign_to=floor
        )
        
        # Add furniture
        
        # Sofa
        sofa_z = room_size * 0.3
        sofa = _create_and_track(
            create_advanced_model,
            model_type="chair",  # Using chair model for now, but scaled to sofa size
            name=f"{name}_sofa",
            translate=[0, 0, sofa_z],
            scale=3.0,
            parameters={
                'seat_width': 6.0,
                'seat_depth': 2.5,
                'seat_height': 1.0,
                'back_height': 2.0
            }
        )
        
        # Coffee table
        table_z = sofa_z - 3.0
        coffee_table = cmds.polyCube(
            name=f"{name}_coffee_table",
            width=4.0,
            height=1.0,
            depth=2.0
        )[0]
        cmds.move(0, 0.5, table_z, coffee_table)
        created_objects.append(coffee_table)
        cmds.parent(coffee_table, scene_group)
        
        # Table material
        _create_and_track(
            create_material,
            material_type="wood",
            name=f"{name}_table_material",
            color=[0.6, 0.4, 0.3],
            assign_to=coffee_table
        )
        
        # TV and stand
        tv_z = -room_size * 0.4
        tv_stand = cmds.polyCube(
            name=f"{name}_tv_stand",
            width=5.0,
            height=1.5,
            depth=1.5
        )[0]
        cmds.move(0, 0.75, tv_z, tv_stand)
        created_objects.append(tv_stand)
        cmds.parent(tv_stand, scene_group)
        
        tv = cmds.polyCube(
            name=f"{name}_tv",
            width=4.5,
            height=2.5,
            depth=0.2
        )[0]
        cmds.move(0, 2.5, tv_z - 0.1, tv)
        created_objects.append(tv)
        cmds.parent(tv, scene_group)
        
        # TV materials
        _create_and_track(
            create_material,
            material_type="wood",
            name=f"{name}_tv_stand_material",
            color=[0.3, 0.2, 0.15],  # Dark wood
            assign_to=tv_stand
        )
        
        _create_and_track(
            create_material,
            material_type="lambert",
            name=f"{name}_tv_material",
            color=[0.05, 0.05, 0.05],  # Near black
            assign_to=tv
        )
        
        # Add some chairs if room is big enough
        if room_size >= 20 and furniture_density > 0.5:
            chair_positions = [
                [-room_size * 0.25, 0, sofa_z - 2.0],  # Left of sofa
                [room_size * 0.25, 0, sofa_z - 2.0]    # Right of sofa
            ]
            
            for i, pos in enumerate(chair_positions):
                chair = _create_and_track(
                    create_advanced_model,
                    model_type="chair",
                    name=f"{name}_chair_{i}",
                    translate=pos,
                    rotate=[0, 180, 0],  # Facing sofa
                    parameters={
                        'seat_width': 2.0,
                        'seat_depth': 2.0,
                        'seat_height': 1.0,
                        'back_height': 2.0
                    }
                )
        
        # Add a rug under the coffee table
        rug = cmds.polyPlane(
            name=f"{name}_rug",
            width=8.0,
            height=5.0
        )[0]
        cmds.move(0, 0.05, sofa_z - 1.0, rug)
        created_objects.append(rug)
        cmds.parent(rug, scene_group)
        
        # Rug material
        rug_colors = [
            [0.8, 0.2, 0.2],  # Red
            [0.2, 0.4, 0.8],  # Blue
            [0.8, 0.7, 0.2]   # Gold
        ]
        _create_and_track(
            create_material,
            material_type="lambert",
            name=f"{name}_rug_material",
            color=random.choice(rug_colors),
            assign_to=rug
        )
        
        return {
            "success": True,
            "name": scene_group,
            "scene_type": "living_room",
            "objects_count": len(created_objects)
        }
    
    elif scene_type.lower() == "office":
        # Get office parameters
        office_size = parameters.get('office_size', 30.0)
        desks_count = parameters.get('desks_count', 4)
        modern_style = parameters.get('modern_style', True)
        
        # Create office room (floor, walls, ceiling)
        floor = cmds.polyPlane(name=f"{name}_floor", width=office_size, height=office_size)[0]
        created_objects.append(floor)
        cmds.parent(floor, scene_group)
        
        wall_height = 10.0
        
        # Create 4 walls
        for i, (pos, rot) in enumerate([
            ([0, wall_height/2, -office_size/2], [0, 0, 0]),      # Back wall
            ([0, wall_height/2, office_size/2], [0, 180, 0]),     # Front wall
            ([-office_size/2, wall_height/2, 0], [0, 90, 0]),     # Left wall
            ([office_size/2, wall_height/2, 0], [0, -90, 0])      # Right wall
        ]):
            wall = cmds.polyPlane(
                name=f"{name}_wall_{i}",
                width=office_size,
                height=wall_height
            )[0]
            cmds.move(pos[0], pos[1], pos[2], wall)
            cmds.rotate(rot[0], rot[1], rot[2], wall)
            created_objects.append(wall)
            cmds.parent(wall, scene_group)
        
        # Create ceiling
        ceiling = cmds.polyPlane(name=f"{name}_ceiling", width=office_size, height=office_size)[0]
        cmds.move(0, wall_height, 0, ceiling)
        cmds.rotate(180, 0, 0, ceiling)
        created_objects.append(ceiling)
        cmds.parent(ceiling, scene_group)
        
        # Create wall and floor materials
        _create_and_track(
            create_material,
            material_type="lambert",
            name=f"{name}_wall_material",
            color=[0.85, 0.85, 0.85],  # Light gray
            assign_to=[f"{name}_wall_0", f"{name}_wall_1", f"{name}_wall_2", f"{name}_wall_3", f"{name}_ceiling"]
        )
        
        _create_and_track(
            create_material,
            material_type="lambert",
            name=f"{name}_floor_material",
            color=[0.7, 0.7, 0.7],  # Gray for office carpet
            assign_to=floor
        )
        
        # Add office desks in a grid pattern
        desk_grid_size = math.ceil(math.sqrt(desks_count))
        desk_spacing = office_size * 0.7 / desk_grid_size
        
        desk_start_x = -desk_spacing * (desk_grid_size - 1) / 2
        desk_start_z = -desk_spacing * (desk_grid_size - 1) / 2
        
        desk_count = 0
        for row in range(desk_grid_size):
            for col in range(desk_grid_size):
                if desk_count >= desks_count:
                    break
                
                desk_x = desk_start_x + col * desk_spacing
                desk_z = desk_start_z + row * desk_spacing
                
                # Randomize orientation
                desk_rot_y = random.choice([0, 90, 180, 270])
                
                # Create desk (simple cube for now)
                desk_width = 4.0
                desk_depth = 2.0
                desk_height = 0.75
                
                desk = cmds.polyCube(
                    name=f"{name}_desk_{desk_count}",
                    width=desk_width,
                    height=desk_height,
                    depth=desk_depth
                )[0]
                cmds.move(desk_x, desk_height/2, desk_z, desk)
                cmds.rotate(0, desk_rot_y, 0, desk)
                created_objects.append(desk)
                cmds.parent(desk, scene_group)
                
                # Create desk material
                desk_color = [0.8, 0.8, 0.8] if modern_style else [0.6, 0.4, 0.2]
                _create_and_track(
                    create_material,
                    material_type="lambert" if modern_style else "wood",
                    name=f"{name}_desk_{desk_count}_material",
                    color=desk_color,
                    assign_to=desk
                )
                
                # Create chair for this desk
                chair_offset_x = 0
                chair_offset_z = 1.5
                
                # Adjust chair position based on desk rotation
                if desk_rot_y == 0:
                    chair_offset_z = 1.5
                elif desk_rot_y == 90:
                    chair_offset_x = -1.5
                    chair_offset_z = 0
                elif desk_rot_y == 180:
                    chair_offset_z = -1.5
                elif desk_rot_y == 270:
                    chair_offset_x = 1.5
                    chair_offset_z = 0
                
                chair = _create_and_track(
                    create_advanced_model,
                    model_type="chair",
                    name=f"{name}_chair_{desk_count}",
                    translate=[desk_x + chair_offset_x, 0, desk_z + chair_offset_z],
                    rotate=[0, desk_rot_y, 0],
                    parameters={
                        'seat_width': 1.5,
                        'seat_depth': 1.5,
                        'seat_height': 1.0,
                        'back_height': 1.8
                    }
                )
                
                # Create computer monitor on desk
                monitor_height = 0.7
                monitor_width = 1.2
                monitor_depth = 0.1
                
                monitor_offset_x = 0
                monitor_offset_z = -0.7
                
                # Adjust monitor position based on desk rotation
                if desk_rot_y == 0:
                    monitor_offset_z = -0.7
                elif desk_rot_y == 90:
                    monitor_offset_x = 0.7
                    monitor_offset_z = 0
                elif desk_rot_y == 180:
                    monitor_offset_z = 0.7
                elif desk_rot_y == 270:
                    monitor_offset_x = -0.7
                    monitor_offset_z = 0
                
                monitor = cmds.polyCube(
                    name=f"{name}_monitor_{desk_count}",
                    width=monitor_width,
                    height=monitor_height,
                    depth=monitor_depth
                )[0]
                cmds.move(
                    desk_x + monitor_offset_x,
                    desk_height + monitor_height/2,
                    desk_z + monitor_offset_z,
                    monitor
                )
                cmds.rotate(0, desk_rot_y, 0, monitor)
                created_objects.append(monitor)
                cmds.parent(monitor, scene_group)
                
                # Create monitor material
                _create_and_track(
                    create_material,
                    material_type="lambert",
                    name=f"{name}_monitor_{desk_count}_material",
                    color=[0.1, 0.1, 0.1],  # Dark gray/black
                    assign_to=monitor
                )
                
                desk_count += 1
        
        # Add some office cabinets along the back wall
        cabinet_count = desks_count // 2
        cabinet_width = office_size * 0.8 / cabinet_count
        cabinet_start_x = -office_size * 0.4 + cabinet_width/2
        
        for i in range(cabinet_count):
            cabinet_x = cabinet_start_x + i * cabinet_width
            cabinet_z = -office_size * 0.45  # Near back wall
            
            cabinet = cmds.polyCube(
                name=f"{name}_cabinet_{i}",
                width=cabinet_width * 0.9,
                height=2.0,
                depth=0.8
            )[0]
            cmds.move(cabinet_x, 1.0, cabinet_z, cabinet)
            created_objects