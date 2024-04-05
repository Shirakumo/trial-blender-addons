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
    filter: bpy.props.StringProperty(
        name="Filter",
        default="T",
        description="A class filter to apply to the trigger volume")

    def customize_layout(self, layout):
        pass

    def customize_object(self, obj):
        pass
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'shape', expand=True)
        layout.prop(self, "filter", expand=True)
        self.customize_layout(layout)
    
    def execute(self, context):
        use_enter_edit_mode = bpy.context.preferences.edit.use_enter_edit_mode
        bpy.context.preferences.edit.use_enter_edit_mode = False

        bpy.ops.mesh.primitive_cube_add(calc_uvs=False)
        bpy.ops.rigidbody.objects_add()
        obj = bpy.context.selected_objects[0]
        obj.name = self.bl_label
        obj.color = (1, 0, 1, 1)
        obj.hide_render = True
        obj.show_bounds = True
        obj.display_type = "BOUNDS"
        obj.display_bounds_type = self.shape
        obj.rigid_body.collision_shape = self.shape
        obj.khr_physics_extra_props.is_trigger = True
        obj.shirakumo_trial_physics_props.filter = self.filter
        self.customize_object(obj)
        
        if use_enter_edit_mode:
            bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.context.preferences.edit.use_enter_edit_mode = use_enter_edit_mode
        return {'FINISHED'}

class SHIRAKUMO_TRIAL_OT_add_trigger(GenericTrigger):
    bl_idname = "shirakumo_trial.add_trigger"
    bl_label = "Trigger"
    bl_description = "Construct a trigger volume"
    
    form: bpy.props.StringProperty(
        name="Lisp Form",
        default="",
        description="The Lisp form to execute on trigger")

    def customize_object(self, obj):
        obj.shirakumo_trial_physics_props.type = 'TRIGGER'
        obj.shirakumo_trial_physics_props.form = self.form

    def customize_layout(self, layout):
        layout.prop(self, 'form', expand=True)

class SHIRAKUMO_TRIAL_OT_add_spawner(GenericTrigger):
    bl_idname = "shirakumo_trial.add_spawner"
    bl_label = "Spawner"
    bl_description = "Construct a spawn volume"
    
    spawn: bpy.props.StringProperty(
        name="Item",
        default="",
        description="The item to spawn")
    spawn_count: bpy.props.IntProperty(
        name="Count",
        default=1, min=1,
        description="The number of items to spawn")
    auto_deactivate: bpy.props.BoolProperty(
        name="Auto-Deactivate",
        default=True,
        description="Whether to deactivate the trigger after all its items have been removed")
    respawn_cooldown: bpy.props.FloatProperty(
        name="Respawn Cooldown",
        default=0.0, min=0.0, unit='TIME',
        description="The number of seconds to wait between the last item was removed before respawning")

    def customize_object(self, obj):
        obj.shirakumo_trial_physics_props.type = 'SPAWNER'
        obj.shirakumo_trial_physics_props.spawn = self.spawn
        obj.shirakumo_trial_physics_props.spawn_count = self.spawn_count
        obj.shirakumo_trial_physics_props.auto_deactivate = self.auto_deactivate
        obj.shirakumo_trial_physics_props.respawn_cooldown = self.respawn_cooldown

    def customize_layout(self, layout):
        layout.prop(self, 'auto_deactivate', expand=True)
        layout.prop(self, 'spawn', expand=True)
        layout.prop(self, 'spawn_count', expand=True)
        layout.prop(self, 'respawn_cooldown', expand=True)

class SHIRAKUMO_TRIAL_OT_add_kill_volume(GenericTrigger):
    bl_idname = "shirakumo_trial.add_kill_volume"
    bl_label = "Kill Volume"
    bl_description = "Construct a kill volume"
    
    kill_type: bpy.props.StringProperty(
        name="Type",
        default="T",
        description="The type name of things to despawn")

    def customize_object(self, obj):
        obj.shirakumo_trial_physics_props.type = 'KILLVOLUME'
        obj.shirakumo_trial_physics_props.kill_type = self.kill_type

    def customize_layout(self, layout):
        layout.prop(self, 'kill_type', expand=True)

class SHIRAKUMO_TRIAL_OT_add_checkpoint(GenericTrigger):
    bl_idname = "shirakumo_trial.add_checkpoint"
    bl_label = "Checkpoint"
    bl_description = "Construct a checkpoint"
    
    def customize_object(self, obj):
        obj.shirakumo_trial_physics_props.type = 'CHECKPOINT'
        child = bpy.data.objects.new('Spawnpoint', None)
        obj.users_collection[-1].objects.link(child)
        child.empty_display_type = 'SINGLE_ARROW'
        child.location = obj.location
        child.parent = obj
        
    def customize_layout(self, layout):
        pass

class SHIRAKUMO_TRIAL_MT_triggers_add(bpy.types.Menu):
    bl_idname = "SHIRAKUMO_TRIAL_MT_triggers_add"
    bl_label = "Triggers"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        layout.operator("shirakumo_trial.add_trigger", text="Trigger", icon="SEQUENCE")
        layout.operator("shirakumo_trial.add_spawner", text="Spawner", icon="GHOST_ENABLED")
        layout.operator("shirakumo_trial.add_kill_volume", text="Kill Volume", icon="GHOST_DISABLED")
        layout.operator("shirakumo_trial.add_checkpoint", text="Checkpoint", icon="CHECKBOX_HLT")
        
def menu_func(self, context):
    layout = self.layout
    layout.operator_context = 'INVOKE_REGION_WIN'
    layout.separator()
    layout.menu("SHIRAKUMO_TRIAL_MT_triggers_add", text="Triggers", icon="DECORATE")

class SHIRAKUMO_TRIAL_physics_properties(bpy.types.PropertyGroup):
    type: bpy.props.EnumProperty(
        name="Type",
        default="NONE",
        description="The type of trigger volume this object is",
        items=[
            ("NONE", "None", "SEQUENCE", 0),
            ("TRIGGER", "Trigger", "", 1),
            ("SPAWNER", "Spawner", "GHOST_ENABLED", 2),
            ("KILLVOLUME", "Kill Volume", "GHOST_DISABLED", 3),
            ("CHECKPOINT", "Checkpoint", "CHECKBOX_HLT", 4),
        ])
    filter: bpy.props.StringProperty(
        name="Filter",
        default="T",
        description="A class filter to apply to the trigger volume")
    form: bpy.props.StringProperty(
        name="Lisp Form",
        default="",
        description="The Lisp form to evaluate when the trigger is hit")
    spawn: bpy.props.StringProperty(
        name="Item",
        default="",
        description="A Lisp form identifying the item to spawn")
    spawn_count: bpy.props.IntProperty(
        name="Spawn Count",
        default=1, min=1,
        description="The number of items to spawn")
    respawn_cooldown: bpy.props.FloatProperty(
        name="Respawn Cooldown",
        default=0.0, min=0.0, unit='TIME',
        description="The number of seconds to wait between a spawned item being removed and it being respawned")
    auto_deactivate: bpy.props.BoolProperty(
        name="Auto-Deactivate",
        default=True,
        description="Whether the trigger should deactivate itself when all its spawned items have been removed")
    kill_type: bpy.props.StringProperty(
        name="Type",
        description="The type name of things to despawn",
        default="T")
    virtual: bpy.props.BoolProperty(
        name="Virtual",
        default=False,
        description="If true the object won't be visible, but will be participating in physics interactions")

class SHIRAKUMO_TRIAL_PT_physics_panel(bpy.types.Panel):
    bl_idname = "SHIRAKUMO_TRIAL_PT_physics_panel"
    bl_label = "Trial Extensions"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "physics"
    
    @classmethod
    def poll(cls, context):
        if context.object and context.object.rigid_body:
            return True
        return None

    def draw(self, context):
        obj = context.object
        layout = self.layout
        layout.use_property_split = True
        flow = layout.grid_flow(row_major=True, columns=0, even_columns=True, even_rows=False, align=True)

        if context.object.khr_physics_extra_props.is_trigger:
            flow.column().prop(obj.shirakumo_trial_physics_props, "type")
            flow.column().prop(obj.shirakumo_trial_physics_props, "filter")
            if obj.shirakumo_trial_physics_props.type == 'TRIGGER':
                flow.column().prop(obj.shirakumo_trial_physics_props, "form")
            elif obj.shirakumo_trial_physics_props.type == 'SPAWNER':
                flow.column().prop(obj.shirakumo_trial_physics_props, "auto_deactivate")
                flow.column().prop(obj.shirakumo_trial_physics_props, "spawn")
                flow.column().prop(obj.shirakumo_trial_physics_props, "spawn_count")
                flow.column().prop(obj.shirakumo_trial_physics_props, "respawn_cooldown")
            elif obj.shirakumo_trial_physics_props.type == 'KILLVOLUME':
                flow.column().prop(obj.shirakumo_trial_physics_props, "kill_type")
            elif obj.shirakumo_trial_physics_props.type == 'CHECKPOINT':
                pass
        else:
            flow.column().prop(obj.shirakumo_trial_physics_props, "virtual")

registered_classes = [
    SHIRAKUMO_TRIAL_OT_add_trigger,
    SHIRAKUMO_TRIAL_OT_add_spawner,
    SHIRAKUMO_TRIAL_OT_add_kill_volume,
    SHIRAKUMO_TRIAL_OT_add_checkpoint,
    SHIRAKUMO_TRIAL_MT_triggers_add,
    SHIRAKUMO_TRIAL_physics_properties,
    SHIRAKUMO_TRIAL_PT_physics_panel,
]

def register():
    for cls in registered_classes:
        bpy.utils.register_class(cls)
    bpy.types.VIEW3D_MT_add.append(menu_func)
    bpy.types.Object.shirakumo_trial_physics_props = bpy.props.PointerProperty(
        type=SHIRAKUMO_TRIAL_physics_properties)

def unregister():
    del bpy.types.Object.shirakumo_trial_physics_props
    bpy.types.VIEW3D_MT_add.remove(menu_func)
    for cls in registered_classes:
        bpy.utils.unregister_class(cls)
    
