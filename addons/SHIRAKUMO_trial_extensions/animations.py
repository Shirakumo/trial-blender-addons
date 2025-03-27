import bpy

def ensure_track_for_property(obj, base, prop, interpolation="CONSTANT", intended=True):
    data_path = base+"."+prop
    action = obj.animation_data.action
    fcurves = action.layers[0].strips[0].channelbag(action.slots[0]).fcurves
    for fcurve in fcurves:
        if fcurve.data_path == data_path:
            if intended == True or prop in intended:
                return fcurve
            else:
                fcurves.remove(fcurve)
                return None
    if intended == True or prop in intended:
        fcurve = fcurves.new(data_path)
        range = action.frame_range
        fcurve.keyframe_points.insert(frame=range[0], value=0.0).interpolation = interpolation
        fcurve.keyframe_points.insert(frame=range[1], value=0.0).interpolation = interpolation
        return fcurve
    return None

def ensure_tracks_for_rig(obj, tracks=True):
    base = "data.shirakumo_trial_extra_props"
    ensure_track_for_property(obj, base, "cancelable", "CONSTANT", tracks)
    ensure_track_for_property(obj, base, "invincible", "CONSTANT", tracks)
    ensure_track_for_property(obj, base, "damage_target", "LINEAR", tracks)
    ensure_track_for_property(obj, base, "stun_target", "LINEAR", tracks)
    ensure_track_for_property(obj, base, "knock_target", "CONSTANT", tracks)
    ensure_track_for_property(obj, base, "lock_target", "CONSTANT", tracks)
    ensure_track_for_property(obj, base, "lock_camera", "CONSTANT", tracks)

def animation_type_changed(self, context):
    obj = context.object
    if obj.animation_data != None:
        if self.type == "PHYSICAL":
            ensure_tracks_for_rig(obj)
        elif self.type == "BLOCKING":
            ensure_tracks_for_rig(obj, ["cancelable", "invincible"])
        else:
            ensure_tracks_for_rig(obj, [])

class SHIRAKUMO_TRIAL_action_properties(bpy.types.PropertyGroup):
    type: bpy.props.EnumProperty(
        name="Type",
        items=[
            ("DEFAULT", "Default", "", 1),
            ("BLOCKING", "Blocking", "", 2),
            ("PHYSICAL", "Physical", "", 3),
            ("ADDITIVE", "Additive", "", 4)
        ],
        default="DEFAULT", options=set(),
        update=animation_type_changed,
        description="The way this animation is interpreted by the engine")
    velocity_scale: bpy.props.FloatProperty(
        name="Velocity Scale",
        default=1.0, min=0, options=set(),
        description="The scaling factor of the root motion velocity")
    loop_animation: bpy.props.BoolProperty(
        name="Loop Animation",
        default=True, options=set(),
        description="Whether to loop the animation or stick to the last frame on end")
    next_animation: bpy.props.StringProperty(
        name="Next Animation",
        default="", options=set(),
        description="The name of the animation to queue after this one completes")
    blend_duration: bpy.props.FloatProperty(
        name="Blend Duration",
        default=0.2, min=0.0, subtype='TIME', options=set(),
        description="The default duration of the blend when switching to this animation")

class SHIRAKUMO_TRIAL_armature_properties(bpy.types.PropertyGroup):
    cancelable: bpy.props.BoolProperty(name="Cancelable", default=True, options={'ANIMATABLE'})
    invincible: bpy.props.BoolProperty(name="Invincible", default=False, options={'ANIMATABLE'})
    damage_target: bpy.props.FloatProperty(name="Target Damage", default=0.0, min=0, options={'ANIMATABLE'})
    stun_target: bpy.props.FloatProperty(name="Target Stun", default=0.0, min=0, options={'ANIMATABLE'})
    knock_target: bpy.props.BoolProperty(name="Target Knockback", default=False, options={'ANIMATABLE'})
    lock_target: bpy.props.BoolProperty(name="Lock Target", default=False, options={'ANIMATABLE'})
    lock_camera: bpy.props.BoolProperty(name="Lock Camera", default=False, options={'ANIMATABLE'})

class SHIRAKUMO_TRIAL_PT_action_panel(bpy.types.Panel):
    bl_idname = "SHIRAKUMO_TRIAL_PT_animation_panel"
    bl_label = "Trial Extensions"
    bl_space_type = "NLA_EDITOR"
    bl_region_type = "UI"
    bl_context = "animation"
    def draw(self, context):
        if context.object.animation_data == None or context.object.animation_data.action == None:
            return
        layout = self.layout
        layout.use_property_split = True
        flow = layout.grid_flow(row_major=True, columns=0, even_columns=True, even_rows=False, align=True)
        obj = context.object.animation_data.action
        flow.column().prop(obj.shirakumo_trial_extra_props, "type")
        if obj.shirakumo_trial_extra_props.type != "ADDITIVE":
            flow.column().prop(obj.shirakumo_trial_extra_props, "loop_animation")
            col = flow.column()
            col.enabled = not obj.shirakumo_trial_extra_props.loop_animation
            col.prop(obj.shirakumo_trial_extra_props, "next_animation")
            flow.column().prop(obj.shirakumo_trial_extra_props, "blend_duration")
        if obj.shirakumo_trial_extra_props.type == "PHYSICAL":
            flow.column().prop(obj.shirakumo_trial_extra_props, "velocity_scale")

registered_classes = [
    SHIRAKUMO_TRIAL_action_properties,
    SHIRAKUMO_TRIAL_armature_properties,
    SHIRAKUMO_TRIAL_PT_action_panel,
]

def register():
    for cls in registered_classes:
        bpy.utils.register_class(cls)
    bpy.types.Action.shirakumo_trial_extra_props = bpy.props.PointerProperty(
        type=SHIRAKUMO_TRIAL_action_properties)
    bpy.types.Armature.shirakumo_trial_extra_props = bpy.props.PointerProperty(
        type=SHIRAKUMO_TRIAL_armature_properties)

def unregister():
    for cls in registered_classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Action.shirakumo_trial_extra_props
    del bpy.types.Armature.shirakumo_trial_extra_props
