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

class ReBake(bpy.types.Operator):
    bl_idname = "shirakumo_trial.rebake"
    bl_label = "ReBake Selected"
    
    @classmethod
    def poll(cls, context):
        for obj in context.selected_objects:
            if obj.type == 'MESH':
                return True
        return None
    
    def execute(self, context):
        for obj in context.selected_objects:
            rebake(obj)

class ReBakeAll(bpy.types.Operator):
    bl_idname = "shirakumo_trial.rebake_all"
    bl_label = "ReBake Selected"
    def execute(self, context):
        rebake_all()

class ReBakeAndExport(bpy.types.Operator):
    bl_idname = "shirakumo_trial.rebake_and_export"
    bl_label = "ReBake Selected"
    def execute(self, context):
        rebake_all()
        bpy.ops.export_scene.gltf(check_existing=False)

class SHIRAKUMO_PT_bake_panel(bpy.types.Panel):
    bl_idname = "SHIRAKUMO_PT_bake_panel"
    bl_label = "Rebake"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Edit"
    bl_context = "objectmode"

    def draw(self, context):
        obj = context.object
        layout = self.layout
        flow = layout.grid_flow(row_major=True, columns=0, even_columns=True, even_rows=False, align=True)
        flow.column().operator("shirakumo_trial.rebake", text="ReBake Selected")
        flow.column().operator("shirakumo_trial.rebake_all", text="ReBake All")
        flow.column().operator("shirakumo_trial.rebake_and_export", text="ReBake & Export")

registered_classes = [
    ReBake,
    ReBakeAll,
    ReBakeAndExport,
    SHIRAKUMO_PT_bake_panel,
]

def register():
    for cls in registered_classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in registered_classes:
        bpy.utils.unregister_class(cls)
