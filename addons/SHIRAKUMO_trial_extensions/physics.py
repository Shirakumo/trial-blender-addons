import bpy
import blf
import os
from bpy_extras import object_utils,view3d_utils
from math import radians,cos

def link_to_object_collection(obj, new):
    for collection in obj.users_collection:
        if collection.name != 'RigidBodyWorld':
            collection.objects.link(new)

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
        layout.prop(self, 'shape', expand=False)
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
        link_to_object_collection(obj, child)
        child.empty_display_type = 'ARROWS'
        child.location = obj.location
        child.parent = obj
        
    def customize_layout(self, layout):
        pass

class SHIRAKUMO_TRIAL_OT_add_progression_trigger(GenericTrigger):
    bl_idname = "shirakumo_trial.add_progression_trigger"
    bl_label = "Progression"
    bl_description = "Construct a progression trigger"

    state: bpy.props.StringProperty(
        name="State",
        default="progression",
        description="The state variable to update")
    value: bpy.props.FloatProperty(
        name="Value",
        default=1.0,
        description="The value to modify the state by")
    mode: bpy.props.EnumProperty(
        name="Mode",
        items=[
            ("INC", "+", "", 1),
            ("DEC", "-", "", 2),
            ("SET", "=", "", 3),
        ],
        default="INC",
        description="The way to update the state by the value")
    condition: bpy.props.StringProperty(
        name="Condition",
        default="T",
        description="The condition that must be true for the state update to happen")

    def customize_object(self, obj):
        obj.shirakumo_trial_physics_props.type = 'PROGRESSION'
        obj.shirakumo_trial_physics_props.state = self.state
        obj.shirakumo_trial_physics_props.value = self.value
        obj.shirakumo_trial_physics_props.mode = self.mode
        obj.shirakumo_trial_physics_props.condition = self.condition

    def customize_layout(self, layout):
        layout.prop(self, 'state', expand=True)
        layout.prop(self, 'value', expand=True)
        layout.prop(self, 'mode', expand=False)
        layout.prop(self, 'condition', expand=True)

class SHIRAKUMO_TRIAL_OT_add_camera_trigger(GenericTrigger):
    bl_idname = "shirakumo_trial.add_camera_trigger"
    bl_label = "Camera"
    bl_description = "Construct a camera trigger"
    
    camera_state: bpy.props.EnumProperty(
        name="State",
        items=[
            ("FREE", "Free", "", 1),
            ("FIXED", "Fixed", "", 2),
            ("ANIMATED", "Animated", "", 3),
        ],
        default="FREE",
        description="The state to switch the camera into")
    target: bpy.props.StringProperty(
        name="Target",
        default="",
        description="The target of the camera change")

    def customize_object(self, obj):
        obj.shirakumo_trial_physics_props.type = 'CAMERA'
        obj.shirakumo_trial_physics_props.camera_state = self.camera_state
        obj.shirakumo_trial_physics_props.target = self.target
        pivot = bpy.data.objects.new('CameraPivot', None)
        link_to_object_collection(obj, pivot)
        pivot.empty_display_type = 'CIRCLE'
        pivot.location = obj.location
        pivot.rotation_euler = (radians(90), 0, 0)
        pivot.parent = obj
        pointer = bpy.data.objects.new('CameraPivotPointer', None)
        link_to_object_collection(obj, pointer)
        pointer.empty_display_type = 'SINGLE_ARROW'
        pointer.location = pivot.location
        pointer.location[0] += 1
        pointer.rotation_euler = (0, radians(-90), 0)
        pointer.scale = [0.5,0.5,0.5]
        pointer.parent = pivot
        # Apply defaults
        default = bpy.context.scene.shirakumo_trial_file_properties.default_camera_offset
        pivot.location[2] += default[0]*cos(default[2])
        pivot.rotation_euler[2] = default[1]
        pivot.scale = [default[0], default[0], default[0]]

    def customize_layout(self, layout):
        layout.prop(self, 'camera_state', expand=True)
        layout.prop(self, 'target', expand=True)
        

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
        layout.operator("shirakumo_trial.add_progression_trigger", text="Progression", icon="TRACKING_FORWARDS")
        layout.operator("shirakumo_trial.add_camera_trigger", text="Camera", icon="VIEW_CAMERA")
        
def menu_func(self, context):
    layout = self.layout
    layout.operator_context = 'INVOKE_REGION_WIN'
    layout.separator()
    layout.menu("SHIRAKUMO_TRIAL_MT_triggers_add", text="Triggers", icon="DECORATE")

def trigger_icon(obj):
    props = obj.shirakumo_trial_physics_props
    if props.type == "NONE": return ""
    if props.type == "TRIGGER":
        return "\uf06a"
    if props.type == "SPAWNER":
        if not props.auto_deactivate: return "\uf1b8"
        return "\uf019"
    if props.type == "KILLVOLUME":
        return "\uf714"
    if props.type == "CHECKPOINT":
        if obj.name == "Start": return "\uf144"
        if obj.name == "End": return "\uf11e"
        return "\uf058"
    if props.type == "PROGRESSION":
        if props.mode == "INC": return "\uf051"
        if props.mode == "DEC": return "\uf048"
        return "\uf0ae"
    if props.type == "CAMERA":
        if props.camera_state == "FREE": return "\ue0d8"
        if props.camera_state == "ANIMATED": return "\ue131"
        return "\uf030"
    if props.type == "INTERACTABLE":
        if props.interaction_kind == "PICKUP": return "\uf4be"
        if props.interaction_kind == "INSPECTABLE": return "\uf002"
        if props.interaction_kind == "USABLE": return "\uf25a"
        if props.interaction_kind == "BUTTON": return "\uf25a"
        return "\uf256"
    return ""

class SHIRAKUMO_TRIAL_physics_properties(bpy.types.PropertyGroup):
    type: bpy.props.EnumProperty(
        name="Type",
        default="NONE", options=set(),
        description="The type of trigger volume this object is",
        items=[
            ("NONE", "None", "SEQUENCE", 0),
            ("TRIGGER", "Trigger", "", 1),
            ("SPAWNER", "Spawner", "GHOST_ENABLED", 2),
            ("KILLVOLUME", "Kill Volume", "GHOST_DISABLED", 3),
            ("CHECKPOINT", "Checkpoint", "CHECKBOX_HLT", 4),
            ("PROGRESSION", "Progression", "TRACKING_FORWARDS", 5),
            ("CAMERA", "Camera", "VIEW_CAMERA", 6),
            ("INTERACTABLE", "Interactable", "VIEWZOOM", 7),
        ])
    filter: bpy.props.StringProperty(
        name="Filter",
        default="T", options=set(),
        description="A class filter to apply to the trigger volume")
    form: bpy.props.StringProperty(
        name="Lisp Form",
        default="", options=set(),
        description="The Lisp form to evaluate when the trigger is hit")
    spawn: bpy.props.StringProperty(
        name="Item",
        default="", options=set(),
        description="A Lisp form identifying the item to spawn")
    spawn_count: bpy.props.IntProperty(
        name="Spawn Count",
        default=1, min=1, options=set(),
        description="The number of items to spawn")
    respawn_cooldown: bpy.props.FloatProperty(
        name="Respawn Cooldown",
        default=0.0, min=0.0, unit='TIME', options=set(),
        description="The number of seconds to wait between a spawned item being removed and it being respawned")
    auto_deactivate: bpy.props.BoolProperty(
        name="Auto-Deactivate",
        default=True, options=set(),
        description="Whether the trigger should deactivate itself when all its spawned items have been removed")
    kill_type: bpy.props.StringProperty(
        name="Type",
        default="T", options=set(),
        description="The type name of things to despawn")
    virtual: bpy.props.BoolProperty(
        name="Virtual",
        default=False, options=set(),
        description="If true the object won't be visible, but will be participating in physics interactions")
    state: bpy.props.StringProperty(
        name="State",
        default="progression", options=set(),
        description="The state variable to update")
    value: bpy.props.FloatProperty(
        name="Value",
        default=1.0, options=set(),
        description="The value to modify the state by")
    mode: bpy.props.EnumProperty(
        name="Mode",
        items=[
            ("INC", "+", "", 1),
            ("DEC", "-", "", 2),
            ("SET", "=", "", 3),
        ],
        default="INC", options=set(),
        description="The way to update the state by the value")
    condition: bpy.props.StringProperty(
        name="Condition",
        default="T", options=set(),
        description="The condition that must be true for the state update to happen")
    camera_state: bpy.props.EnumProperty(
        name="State",
        items=[
            ("FREE", "Free", "", 1),
            ("FIXED", "Fixed", "", 2),
            ("ANIMATED", "Animated", "", 3),
        ],
        default="FREE", options=set(),
        description="The state to switch the camera into")
    target: bpy.props.StringProperty(
        name="Target",
        default="", options=set(),
        description="The target of the camera change")
    offset: bpy.props.FloatVectorProperty(
        name="Offset",
        default=[0,0,0], subtype='EULER', options=set(),
        description="The offset of camera triggers")
    interaction: bpy.props.StringProperty(
        name="Interaction",
        default="", options=set(),
        description="The interaction to trigger for the object.")
    interaction_kind: bpy.props.EnumProperty(
        name="Kind",
        items=[
            ("PICKUP", "Pickup", "", 1),
            ("INSPECTABLE", "Inspectable", "", 2),
            ("USABLE", "Usable", "", 3),
            ("BUTTON", "Button", "", 4),
        ],
        default="INSPECTABLE", options=set(),
        description="The kind of interaction to trigger")

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

        flow.column().prop(obj.shirakumo_trial_physics_props, "type")
        if obj.shirakumo_trial_physics_props.type in ['NONE', 'INTERACTABLE']:
            flow.column().prop(obj.shirakumo_trial_physics_props, "virtual")
        else:
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
        elif obj.shirakumo_trial_physics_props.type == 'PROGRESSION':
            flow.column().prop(obj.shirakumo_trial_physics_props, "state")
            flow.column().prop(obj.shirakumo_trial_physics_props, "value")
            flow.column().prop(obj.shirakumo_trial_physics_props, "mode")
            flow.column().prop(obj.shirakumo_trial_physics_props, "condition")
        elif obj.shirakumo_trial_physics_props.type == 'CAMERA':
            flow.column().prop(obj.shirakumo_trial_physics_props, "camera_state")
            flow.column().prop(obj.shirakumo_trial_physics_props, "target")
            flow.column().prop(obj.shirakumo_trial_physics_props, "offset")
        elif obj.shirakumo_trial_physics_props.type == 'INTERACTABLE':
            flow.column().prop(obj.shirakumo_trial_physics_props, "form")
            flow.column().prop(obj.shirakumo_trial_physics_props, "interaction")
            flow.column().prop(obj.shirakumo_trial_physics_props, "interaction_kind")

class SHIRAKUMO_TRIAL_viewport_render:
    
    def __init__(self):
        self.icon_size = 50.0
        self.font = None
        self.fontpath = os.path.dirname(__file__)+'/fontawesome.ttf'
        if not bpy.app.background:
            self.font = blf.load(self.fontpath)

    def draw_all(self):
        if self.font == None:
            return
        for obj in bpy.data.objects:
            self.draw(obj)
    
    def draw(self, obj):
        if self.font == None:
            return
        if obj.shirakumo_trial_physics_props.type == 'NONE':
            return
        icon = trigger_icon(obj)
        if icon != "":
            # We have to reload the font here because for **whatever reason** the font gets FUCKED when
            # you load a new scene, and this is the easiest way to fix it back up. Sigh.
            self.font = blf.load(self.fontpath)
            position = view3d_utils.location_3d_to_region_2d(bpy.context.region, bpy.context.space_data.region_3d, obj.location)
            (w,h) = blf.dimensions(self.font, icon)
            blf.size(self.font, self.icon_size)
            blf.position(self.font, position[0]-w/2, position[1]-h/2, 0)
            if obj.select_get():
                blf.color(self.font, 1, 0.75, 0, 0.75)
            else:
                blf.color(self.font, 0, 0, 0, 0.5)
            blf.draw(self.font, icon)
        
viewport_render = SHIRAKUMO_TRIAL_viewport_render()

registered_classes = [
    SHIRAKUMO_TRIAL_OT_add_trigger,
    SHIRAKUMO_TRIAL_OT_add_spawner,
    SHIRAKUMO_TRIAL_OT_add_kill_volume,
    SHIRAKUMO_TRIAL_OT_add_checkpoint,
    SHIRAKUMO_TRIAL_OT_add_progression_trigger,
    SHIRAKUMO_TRIAL_OT_add_camera_trigger,
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
    global draw_handler
    draw_handler = bpy.types.SpaceView3D.draw_handler_add(
        viewport_render.draw_all, (), "WINDOW", "POST_PIXEL")

def unregister():
    del bpy.types.Object.shirakumo_trial_physics_props
    bpy.types.VIEW3D_MT_add.remove(menu_func)
    for cls in registered_classes:
        bpy.utils.unregister_class(cls)
    global draw_handler
    bpy.types.SpaceView3D.draw_handler_remove(draw_handler, "WINDOW")
    draw_handler = None
    
