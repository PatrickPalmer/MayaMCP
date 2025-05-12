from typing import Dict, List, Any, Optional


def create_material(
    material_type: str,
    name: str = None,
    color: List[float] = [0.5, 0.5, 0.5],
    parameters: Dict[str, Any] = None,
    assign_to: str = None
) -> Dict[str, Any]:
    """Creates a material in the Maya scene and optionally assigns it to an object.
    
    Available material types:
    - lambert: Basic matte material
    - phong: Shiny material with specular highlights
    - blinn: Similar to phong but with a different specular model
    - metal: Metallic PBR material
    - wood: Procedural wood grain material
    - marble: Procedural marble material
    - chrome: Reflective chrome material
    - glass: Transparent glass material
    - brushed_metal: Brushed metal effect with anisotropic highlights
    - car_paint: Multi-layered car paint with flakes
    
    Parameters is a dictionary containing material-specific settings.
    Example parameters for phong: {'specularColor': [1.0, 1.0, 1.0], 'reflectivity': 0.5}
    Example parameters for wood: {'veinSpread': 0.5, 'veinColor': [0.3, 0.2, 0.1]}
    
    Color is the base color [R, G, B] with values between 0-1.
    
    If assign_to is specified, the material will be assigned to that object.
    """
    import maya.cmds as cmds
    import random
    
    def _validate_vector3d(vec:List[float]):
        return isinstance(vec, list) and len(vec) == 3 and all([isinstance(v, float) for v in vec])
    
    # Validate inputs
    if not _validate_vector3d(color):
        raise ValueError("Invalid color format. Must be a list of 3 float values between 0-1.")
    
    # If assign_to is specified, validate it exists
    if assign_to and not cmds.objExists(assign_to):
        raise ValueError(f"Error: {assign_to} doesn't exist in the scene")
    
    # Set default parameters dict if none provided
    if parameters is None:
        parameters = {}
    
    # Set default name if none provided
    if name is None:
        name = f"{material_type}_mat_{int(random.random() * 1000)}"
    
    # Track created nodes for return value
    created_nodes = []
    
    # Create the material based on type
    if material_type.lower() == "lambert":
        # Create a basic Lambert material
        shader = cmds.shadingNode('lambert', asShader=True, name=name)
        created_nodes.append(shader)
        
        # Set basic color
        cmds.setAttr(f"{shader}.color", color[0], color[1], color[2], type='double3')
        
        # Set additional parameters
        for param, value in parameters.items():
            if cmds.attributeQuery(param, node=shader, exists=True):
                if isinstance(value, list) and len(value) == 3:
                    cmds.setAttr(f"{shader}.{param}", value[0], value[1], value[2], type='double3')
                else:
                    cmds.setAttr(f"{shader}.{param}", value)
    
    elif material_type.lower() == "phong":
        # Create a Phong material
        shader = cmds.shadingNode('phong', asShader=True, name=name)
        created_nodes.append(shader)
        
        # Set basic color
        cmds.setAttr(f"{shader}.color", color[0], color[1], color[2], type='double3')
        
        # Set default phong properties
        specularColor = parameters.get('specularColor', [1.0, 1.0, 1.0])
        reflectivity = parameters.get('reflectivity', 0.5)
        
        cmds.setAttr(f"{shader}.specularColor", specularColor[0], specularColor[1], specularColor[2], type='double3')
        cmds.setAttr(f"{shader}.reflectivity", reflectivity)
        
        # Set additional parameters
        for param, value in parameters.items():
            if param not in ['specularColor', 'reflectivity'] and cmds.attributeQuery(param, node=shader, exists=True):
                if isinstance(value, list) and len(value) == 3:
                    cmds.setAttr(f"{shader}.{param}", value[0], value[1], value[2], type='double3')
                else:
                    cmds.setAttr(f"{shader}.{param}", value)
    
    elif material_type.lower() == "blinn":
        # Create a Blinn material
        shader = cmds.shadingNode('blinn', asShader=True, name=name)
        created_nodes.append(shader)
        
        # Set basic color
        cmds.setAttr(f"{shader}.color", color[0], color[1], color[2], type='double3')
        
        # Set default blinn properties
        specularColor = parameters.get('specularColor', [1.0, 1.0, 1.0])
        reflectivity = parameters.get('reflectivity', 0.5)
        eccentricity = parameters.get('eccentricity', 0.3)
        
        cmds.setAttr(f"{shader}.specularColor", specularColor[0], specularColor[1], specularColor[2], type='double3')
        cmds.setAttr(f"{shader}.reflectivity", reflectivity)
        cmds.setAttr(f"{shader}.eccentricity", eccentricity)
        
        # Set additional parameters
        for param, value in parameters.items():
            if param not in ['specularColor', 'reflectivity', 'eccentricity'] and cmds.attributeQuery(param, node=shader, exists=True):
                if isinstance(value, list) and len(value) == 3:
                    cmds.setAttr(f"{shader}.{param}", value[0], value[1], value[2], type='double3')
                else:
                    cmds.setAttr(f"{shader}.{param}", value)
    
    elif material_type.lower() == "metal":
        # Create a metallic material using aiStandardSurface (if Arnold is available) or fallback to blinn
        if cmds.pluginInfo('mtoa', query=True, loaded=True):
            shader = cmds.shadingNode('aiStandardSurface', asShader=True, name=name)
            created_nodes.append(shader)
            
            # Set as metal
            cmds.setAttr(f"{shader}.base", 1.0)
            cmds.setAttr(f"{shader}.baseColor", color[0], color[1], color[2], type='double3')
            cmds.setAttr(f"{shader}.metalness", 1.0)
            cmds.setAttr(f"{shader}.specular", 1.0)
            cmds.setAttr(f"{shader}.specularRoughness", 0.2)
            
            # Set additional parameters
            roughness = parameters.get('roughness', 0.2)
            cmds.setAttr(f"{shader}.specularRoughness", roughness)
            
            for param, value in parameters.items():
                if param not in ['roughness'] and cmds.attributeQuery(param, node=shader, exists=True):
                    if isinstance(value, list) and len(value) == 3:
                        cmds.setAttr(f"{shader}.{param}", value[0], value[1], value[2], type='double3')
                    else:
                        cmds.setAttr(f"{shader}.{param}", value)
        else:
            # Fallback to blinn
            shader = cmds.shadingNode('blinn', asShader=True, name=name)
            created_nodes.append(shader)
            
            # Make it look metallic with a blinn shader
            cmds.setAttr(f"{shader}.color", color[0], color[1], color[2], type='double3')
            cmds.setAttr(f"{shader}.specularColor", color[0], color[1], color[2], type='double3')
            cmds.setAttr(f"{shader}.reflectivity", 0.7)
            cmds.setAttr(f"{shader}.eccentricity", 0.1)
    
    elif material_type.lower() == "wood":
        # Create a procedural wood material
        shader = cmds.shadingNode('lambert', asShader=True, name=name)
        created_nodes.append(shader)
        
        # Create procedural textures for wood
        wood_noise = cmds.shadingNode('fractal', asTexture=True, name=f"{name}_fractal")
        created_nodes.append(wood_noise)
        
        ramp = cmds.shadingNode('ramp', asTexture=True, name=f"{name}_ramp")
        created_nodes.append(ramp)
        
        place2d = cmds.shadingNode('place2dTexture', asUtility=True, name=f"{name}_place2d")
        created_nodes.append(place2d)
        
        # Connect place2d to fractal
        for attr in ['outUV', 'outUvFilterSize']:
            cmds.connectAttr(f"{place2d}.{attr}", f"{wood_noise}.{attr}")
        for attr in ['coverage', 'translateFrame', 'rotateFrame', 'mirrorU', 'mirrorV', 'stagger', 'wrapU', 'wrapV', 'repeatUV', 'offset', 'rotateUV', 'noiseUV', 'vertexUvOne', 'vertexUvTwo', 'vertexUvThree', 'vertexCameraOne']:
            if cmds.attributeQuery(attr, node=place2d, exists=True) and cmds.attributeQuery(attr, node=wood_noise, exists=True):
                cmds.connectAttr(f"{place2d}.{attr}", f"{wood_noise}.{attr}")
        
        # Configure fractal for wood-like pattern
        cmds.setAttr(f"{place2d}.repeatU", 1)
        cmds.setAttr(f"{place2d}.repeatV", 4)
        
        veinSpread = parameters.get('veinSpread', 0.5)
        veinColor = parameters.get('veinColor', [0.3, 0.2, 0.1])
        
        cmds.setAttr(f"{wood_noise}.amplitude", 0.5)
        cmds.setAttr(f"{wood_noise}.threshold", 0.0)
        cmds.setAttr(f"{wood_noise}.ratio", 0.707)
        cmds.setAttr(f"{wood_noise}.frequencyRatio", 2.0)
        cmds.setAttr(f"{wood_noise}.time", veinSpread)
        
        # Configure ramp for wood color variation
        cmds.setAttr(f"{ramp}.type", 0)  # U Ramp
        cmds.setAttr(f"{ramp}.interpolation", 4)  # Smooth interpolation
        
        # Set ramp colors - base wood color to vein color
        cmds.setAttr(f"{ramp}.colorEntryList[0].color", color[0], color[1], color[2], type='double3')
        cmds.setAttr(f"{ramp}.colorEntryList[0].position", 0)
        cmds.setAttr(f"{ramp}.colorEntryList[1].color", veinColor[0], veinColor[1], veinColor[2], type='double3')
        cmds.setAttr(f"{ramp}.colorEntryList[1].position", 0.5)
        cmds.setAttr(f"{ramp}.colorEntryList[2].color", color[0], color[1], color[2], type='double3')
        cmds.setAttr(f"{ramp}.colorEntryList[2].position", 1)
        
        # Connect fractal to ramp
        cmds.connectAttr(f"{wood_noise}.outColor", f"{ramp}.uvCoord")
        
        # Connect ramp to shader
        cmds.connectAttr(f"{ramp}.outColor", f"{shader}.color")
    
    elif material_type.lower() == "marble":
        # Create a procedural marble material
        shader = cmds.shadingNode('lambert', asShader=True, name=name)
        created_nodes.append(shader)
        
        # Create procedural textures for marble
        marble_noise = cmds.shadingNode('marble', asTexture=True, name=f"{name}_marble")
        created_nodes.append(marble_noise)
        
        place2d = cmds.shadingNode('place2dTexture', asUtility=True, name=f"{name}_place2d")
        created_nodes.append(place2d)
        
        # Connect place2d to marble
        for attr in ['outUV', 'outUvFilterSize']:
            cmds.connectAttr(f"{place2d}.{attr}", f"{marble_noise}.{attr}")
        for attr in ['coverage', 'translateFrame', 'rotateFrame', 'mirrorU', 'mirrorV', 'stagger', 'wrapU', 'wrapV', 'repeatUV', 'offset', 'rotateUV', 'noiseUV', 'vertexUvOne', 'vertexUvTwo', 'vertexUvThree', 'vertexCameraOne']:
            if cmds.attributeQuery(attr, node=place2d, exists=True) and cmds.attributeQuery(attr, node=marble_noise, exists=True):
                cmds.connectAttr(f"{place2d}.{attr}", f"{marble_noise}.{attr}")
        
        # Configure marble texture
        veinSpread = parameters.get('veinSpread', 0.5)
        veinColor = parameters.get('veinColor', [0.1, 0.1, 0.1])
        
        cmds.setAttr(f"{place2d}.repeatU", 1)
        cmds.setAttr(f"{place2d}.repeatV", 1)
        
        cmds.setAttr(f"{marble_noise}.color1", color[0], color[1], color[2], type='double3')
        cmds.setAttr(f"{marble_noise}.color2", veinColor[0], veinColor[1], veinColor[2], type='double3')
        cmds.setAttr(f"{marble_noise}.veinSpread", veinSpread)
        
        # Connect marble to shader
        cmds.connectAttr(f"{marble_noise}.outColor", f"{shader}.color")
    
    elif material_type.lower() == "chrome":
        # Create a chrome material using aiStandardSurface (if Arnold is available) or fallback to blinn
        if cmds.pluginInfo('mtoa', query=True, loaded=True):
            shader = cmds.shadingNode('aiStandardSurface', asShader=True, name=name)
            created_nodes.append(shader)
            
            # Set as chrome
            cmds.setAttr(f"{shader}.base", 1.0)
            cmds.setAttr(f"{shader}.baseColor", color[0], color[1], color[2], type='double3')
            cmds.setAttr(f"{shader}.metalness", 1.0)
            cmds.setAttr(f"{shader}.specular", 1.0)
            cmds.setAttr(f"{shader}.specularRoughness", 0.05)
            
            # Set additional parameters
            roughness = parameters.get('roughness', 0.05)
            cmds.setAttr(f"{shader}.specularRoughness", roughness)
        else:
            # Fallback to blinn
            shader = cmds.shadingNode('blinn', asShader=True, name=name)
            created_nodes.append(shader)
            
            # Make it look like chrome
            cmds.setAttr(f"{shader}.color", color[0], color[1], color[2], type='double3')
            cmds.setAttr(f"{shader}.specularColor", 1, 1, 1, type='double3')
            cmds.setAttr(f"{shader}.reflectivity", 1.0)
            cmds.setAttr(f"{shader}.eccentricity", 0.01)
    
    elif material_type.lower() == "glass":
        # Create a glass material
        if cmds.pluginInfo('mtoa', query=True, loaded=True):
            # Use Arnold if available
            shader = cmds.shadingNode('aiStandardSurface', asShader=True, name=name)
            created_nodes.append(shader)
            
            # Set as glass
            cmds.setAttr(f"{shader}.base", 0.0)
            cmds.setAttr(f"{shader}.baseColor", color[0], color[1], color[2], type='double3')
            cmds.setAttr(f"{shader}.specular", 1.0)
            cmds.setAttr(f"{shader}.specularColor", 1, 1, 1, type='double3')
            cmds.setAttr(f"{shader}.specularRoughness", 0.0)
            cmds.setAttr(f"{shader}.specularIOR", 1.5)
            cmds.setAttr(f"{shader}.transmission", 1.0)
            cmds.setAttr(f"{shader}.transmissionColor", color[0], color[1], color[2], type='double3')
        else:
            # Fallback to phong
            shader = cmds.shadingNode('phong', asShader=True, name=name)
            created_nodes.append(shader)
            
            # Make it look like glass (limited in standard Maya shaders)
            cmds.setAttr(f"{shader}.color", color[0], color[1], color[2], type='double3')
            cmds.setAttr(f"{shader}.transparency", 0.8, 0.8, 0.8, type='double3')
            cmds.setAttr(f"{shader}.reflectedColor", 0.2, 0.2, 0.2, type='double3')
            cmds.setAttr(f"{shader}.reflectivity", 0.5)
    
    elif material_type.lower() == "brushed_metal":
        # Create a brushed metal material with anisotropic highlights
        if cmds.pluginInfo('mtoa', query=True, loaded=True):
            # Use Arnold if available
            shader = cmds.shadingNode('aiStandardSurface', asShader=True, name=name)
            created_nodes.append(shader)
            
            # Set as brushed metal
            cmds.setAttr(f"{shader}.base", 1.0)
            cmds.setAttr(f"{shader}.baseColor", color[0], color[1], color[2], type='double3')
            cmds.setAttr(f"{shader}.metalness", 1.0)
            cmds.setAttr(f"{shader}.specular", 1.0)
            cmds.setAttr(f"{shader}.specularAnisotropy", 0.5)
            cmds.setAttr(f"{shader}.specularRotation", 0.0)
            cmds.setAttr(f"{shader}.specularRoughness", 0.3)
        else:
            # Fallback to anisotropic shader
            shader = cmds.shadingNode('anisotropic', asShader=True, name=name)
            created_nodes.append(shader)
            
            # Set anisotropic properties
            cmds.setAttr(f"{shader}.color", color[0], color[1], color[2], type='double3')
            cmds.setAttr(f"{shader}.reflectivity", 0.5)
            cmds.setAttr(f"{shader}.roughness", 0.3)
            cmds.setAttr(f"{shader}.anisotropicReflectivity", 0.5)
            cmds.setAttr(f"{shader}.correlationX", 0.5)
            cmds.setAttr(f"{shader}.correlationY", 0.0)
            cmds.setAttr(f"{shader}.fresnel", 1)
            cmds.setAttr(f"{shader}.spreadX", 40)
            cmds.setAttr(f"{shader}.spreadY", 10)
    
    elif material_type.lower() == "car_paint":
        # Create a car paint material
        if cmds.pluginInfo('mtoa', query=True, loaded=True):
            # Use Arnold if available
            shader = cmds.shadingNode('aiStandardSurface', asShader=True, name=name)
            created_nodes.append(shader)
            
            # Set as car paint
            cmds.setAttr(f"{shader}.base", 1.0)
            cmds.setAttr(f"{shader}.baseColor", color[0], color[1], color[2], type='double3')
            cmds.setAttr(f"{shader}.specular", 1.0)
            cmds.setAttr(f"{shader}.specularRoughness", 0.1)
            cmds.setAttr(f"{shader}.specularIOR", 1.5)
            cmds.setAttr(f"{shader}.coat", 1.0)
            cmds.setAttr(f"{shader}.coatRoughness", 0.0)
            
            # Create a noise texture for flakes
            flakeColor = parameters.get('flakeColor', [1.0, 1.0, 1.0])
            flakeScale = parameters.get('flakeScale', 100.0)
            flakeIntensity = parameters.get('flakeIntensity', 0.2)
            
            if flakeIntensity > 0:
                flake_noise = cmds.shadingNode('aiNoise', asTexture=True, name=f"{name}_flakes")
                created_nodes.append(flake_noise)
                
                cmds.setAttr(f"{flake_noise}.scaleX", flakeScale)
                cmds.setAttr(f"{flake_noise}.scaleY", flakeScale)
                cmds.setAttr(f"{flake_noise}.scaleZ", flakeScale)
                cmds.setAttr(f"{flake_noise}.octaves", 1)
                cmds.setAttr(f"{flake_noise}.distortion", 0)
                cmds.setAttr(f"{flake_noise}.lacunarity", 2)
                cmds.setAttr(f"{flake_noise}.amplitude", flakeIntensity)
                
                # Create a color mix for flakes
                color_mix = cmds.shadingNode('aiMixRgb', asUtility=True, name=f"{name}_color_mix")
                created_nodes.append(color_mix)
                
                cmds.setAttr(f"{color_mix}.input1", color[0], color[1], color[2], type='double3')
                cmds.setAttr(f"{color_mix}.input2", flakeColor[0], flakeColor[1], flakeColor[2], type='double3')
                
                # Connect nodes
                cmds.connectAttr(f"{flake_noise}.outColorR", f"{color_mix}.mix")
                cmds.connectAttr(f"{color_mix}.outRgb", f"{shader}.baseColor")
        else:
            # Fallback to blinn
            shader = cmds.shadingNode('blinn', asShader=True, name=name)
            created_nodes.append(shader)
            
            # Set car paint like properties
            cmds.setAttr(f"{shader}.color", color[0], color[1], color[2], type='double3')
            cmds.setAttr(f"{shader}.specularColor", 1, 1, 1, type='double3')
            cmds.setAttr(f"{shader}.reflectivity", 0.5)
            cmds.setAttr(f"{shader}.eccentricity", 0.1)
    
    else:
        raise ValueError(f"Unknown material type: {material_type}. Use lambert, phong, blinn, metal, wood, marble, chrome, glass, brushed_metal, or car_paint")
    
    # Create a shading group
    sg = cmds.sets(name=f"{name}SG", empty=True, renderable=True, noSurfaceShader=True)
    created_nodes.append(sg)
    
    # Connect shader to shading group
    cmds.connectAttr(f"{shader}.outColor", f"{sg}.surfaceShader")
    
    # Assign to object if specified
    if assign_to:
        cmds.sets(assign_to, edit=True, forceElement=sg)
    
    return {
        "success": True,
        "name": name,
        "shader": shader,
        "material_type": material_type,
        "shading_group": sg,
        "created_nodes": created_nodes
    }