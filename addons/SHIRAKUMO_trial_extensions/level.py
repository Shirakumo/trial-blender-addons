import bpy

def hide_all(filter):
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            obj.hide_render = filter(obj)

def rebake(obj):
    ## If we have a level object, hide everything but other level objects
    if obj.khr_physics_extra_props.infinite_mass:
        hide_all(lambda obj : not obj.khr_physics_extra_props.infinite_mass)
    ## Otherwise hide everything but this object
    else:
        hide_all(lambda obj : True)
        obj.hide_render = False
    
    previous_selected = bpy.context.selected_objects
    obj.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(island_margin=0.001)
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.bake(type='AO', use_clear=True)
    bpy.context.selected_objects = previous_selected

def rebake_all():
    for obj in bpy.data.objects:
        if obj.type == 'MESH' and (not context.object.rigid_body or
                                   not context.object.khr_physics_extra_props.is_trigger):
            rebake(obj)

def rebake_and_export():
    rebake_all()
    bpy.ops.export_scene.gltf(check_existing=False)

def register():
    pass

def unregister():
    pass
