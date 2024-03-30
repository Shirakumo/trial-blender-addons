import bpy
from bpy_extras import object_utils

class GenericTrigger(bpy.types.Operator, object_utils.AddObjectHelper):
    bl_options = {'REGISTER', 'UNDO', 'PRESET'}
    
    shape: bpy.props.EnumProperty(
        name="Shape",
        description="The shape of the trigger volume",
        items=[
            ("BOX", "Box", "MESH_CUBE", 1),
            ("SPHERE", "Sphere", "MESH_UVSPHERE", 2),
            ("CAPSULE", "Capsule", "MESH_CAPSULE", 3),
            ("CYLINDER", "Cylinder", "MESH_CYLINDER", 4),
        ])

    def customize_layout(self, layout):
        pass

    def customize_object(self, obj):
        pass
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'shape', expand=True)
        self.customize_layout(layout)
    
    def execute(self, context):
        use_enter_edit_mode = bpy.context.preferences.edit.use_enter_edit_mode
        bpy.context.preferences.edit.use_enter_edit_mode = False

        bpy.ops.mesh.primitive_cube_add(calc_uvs=False)
        obj = bpy.context.selected_objects[0]
        obj.name = "Trigger"
        bpy.ops.rigidbody.objects_add()
        obj.color = (1, 0, 1, 1)
        obj.hide_render = True
        obj.show_bounds = True
        obj.display_type = "BOUNDS"
        obj.display_bounds_type = self.shape
        obj.rigid_body.collision_shape = self.shape
        obj.khr_physics_extra_props.is_trigger = True
        self.customize_object(obj)
        
        if use_enter_edit_mode:
            bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.context.preferences.edit.use_enter_edit_mode = use_enter_edit_mode
        return {'FINISHED'}

class AddTrigger(GenericTrigger):
    bl_idname = "shirakumo_trial.add_trigger"
    bl_label = "Trigger"
    bl_description = "Construct a trigger volume"
    
    form: bpy.props.StringProperty(
        name="Lisp Form",
        description="The Lisp form to execute on trigger")

    def customize_object(self, obj):
        obj.shirakumo_trial_trigger_props.type = 'TRIGGER'
        obj.shirakumo_trial_trigger_props.form = self.form

    def customize_layout(self, layout):
        layout.prop(self, 'form', expand=True)

class AddSpawner(GenericTrigger):
    bl_idname = "shirakumo_trial.add_spawner"
    bl_label = "Spawner"
    bl_description = "Construct a spawn volume"
    
    spawn: bpy.props.StringProperty(
        name="Item",
        description="The item to spawn")
    spawn_count: bpy.props.IntProperty(
        name="Count",
        description="The number of items to spawn",
        min=1,
        default=1)
    auto_deactivate: bpy.props.BoolProperty(
        name="Auto-Deactivate",
        description="Whether to deactivate the trigger after all its items have been removed",
        default=True)
    respawn_cooldown: bpy.props.FloatProperty(
        name="Respawn Cooldown",
        description="The number of seconds to wait between the last item was removed before respawning",
        default=0.0)

    def customize_object(self, obj):
        obj.shirakumo_trial_trigger_props.type = 'SPAWNER'
        obj.shirakumo_trial_trigger_props.spawn = self.spawn
        obj.shirakumo_trial_trigger_props.spawn_count = self.spawn_count
        obj.shirakumo_trial_trigger_props.auto_deactivate = self.auto_deactivate
        obj.shirakumo_trial_trigger_props.respawn_cooldown = self.respawn_cooldown

    def customize_layout(self, layout):
        layout.prop(self, 'auto_deactivate', expand=True)
        layout.prop(self, 'spawn', expand=True)
        layout.prop(self, 'spawn_count', expand=True)
        layout.prop(self, 'respawn_cooldown', expand=True)

class AddKillVolume(GenericTrigger):
    bl_idname = "shirakumo_trial.add_kill_volume"
    bl_label = "Kill Volume"
    bl_description = "Construct a kill volume"
    
    kill_type: bpy.props.StringProperty(
        name="Type",
        description="The type name of things to despawn",
        default="T")

    def customize_object(self, obj):
        obj.shirakumo_trial_trigger_props.type = 'KILLVOLUME'
        obj.shirakumo_trial_trigger_props.kill_type = self.kind

    def customize_layout(self, layout):
        layout.prop(self, 'kill_type', expand=True)

class VIEW3D_MT_triggers_add(bpy.types.Menu):
    bl_idname = "VIEW3D_MT_shirakumo_trial_triggers_add"
    bl_label = "Triggers"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        layout.operator("shirakumo_trial.add_trigger", text="Trigger")
        layout.operator("shirakumo_trial.add_spawner", text="Spawner")
        layout.operator("shirakumo_trial.add_kill_volume", text="Kill Volume")
        
def menu_func(self, context):
    layout = self.layout
    layout.operator_context = 'INVOKE_REGION_WIN'
    layout.separator()
    layout.menu("VIEW3D_MT_shirakumo_trial_triggers_add", text="Triggers", icon="DECORATE")

class SHIRAKUMO_trial_trigger_properties(bpy.types.PropertyGroup):
    type: bpy.props.EnumProperty(name="Type", default="NONE", items=[
        ("NONE", "None", "", 0),
        ("TRIGGER", "Trigger", "", 1),
        ("SPAWNER", "Spawner", "", 2),
        ("KILLVOLUME", "Kill Volume", "", 3),
    ])
    form: bpy.props.StringProperty(name="Lisp Form", default="")
    spawn: bpy.props.StringProperty(name="Item", default="")
    spawn_count: bpy.props.IntProperty(name="Spawn Count", default=1, min=1)
    respawn_cooldown: bpy.props.FloatProperty(name="Respawn Cooldown", default=0.0, min=0.0)
    auto_deactivate: bpy.props.BoolProperty(name="Auto-Deactivate", default=True)

class SHIRAKUMO_PT_trigger_panel(bpy.types.Panel):
    bl_idname = "SHIRAKUMO_PT_trigger_panel"
    bl_label = "Trial Trigger Extensions"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "physics"
    
    @classmethod
    def poll(cls, context):
        if context.object and context.object.rigid_body and context.object.khr_physics_extra_props.is_trigger:
            return True
        return None

    def draw(self, context):
        obj = context.object
        layout = self.layout
        layout.use_property_split = True
        flow = layout.grid_flow(row_major=True, columns=0, even_columns=True, even_rows=False, align=True)

        flow.column().prop(obj.shirakumo_trial_trigger_props, "type")
        if obj.shirakumo_trial_trigger_props.type == 'TRIGGER':
            flow.column().prop(obj.shirakumo_trial_trigger_props, "form")
        if obj.shirakumo_trial_trigger_props.type == 'SPAWNER':
            flow.column().prop(obj.shirakumo_trial_trigger_props, "auto_deactivate")
            flow.column().prop(obj.shirakumo_trial_trigger_props, "spawn")
            flow.column().prop(obj.shirakumo_trial_trigger_props, "spawn_count")
            flow.column().prop(obj.shirakumo_trial_trigger_props, "respawn_cooldown")
        if obj.shirakumo_trial_trigger_props.type == 'KILLVOLUME':
            flow.column().prop(obj.shirakumo_trial_trigger_props, "type")

registered_classes = [
    AddTrigger,
    AddSpawner,
    AddKillVolume,
    VIEW3D_MT_triggers_add,
    SHIRAKUMO_trial_trigger_properties,
    SHIRAKUMO_PT_trigger_panel,
]

def register():
    for cls in registered_classes:
        bpy.utils.register_class(cls)
    bpy.types.VIEW3D_MT_add.append(menu_func)
    bpy.types.Object.shirakumo_trial_trigger_props = bpy.props.PointerProperty(
        type=SHIRAKUMO_trial_trigger_properties)

def unregister():
    del bpy.types.Object.shirakumo_trial_trigger_props
    bpy.types.VIEW3D_MT_add.remove(menu_func)
    for cls in registered_classes:
        bpy.utils.unregister_class(cls)
    
