import bpy

def ensure_track_for_property(obj, data_path, interpolation="CONSTANT"):
    action = obj.animation_data.action
    for fcurve in action.fcurves:
        if fcurve.data_path == data_path:
            return fcurve
    fcurve = action.fcurves.new(data_path)
    range = action.frame_range
    fcurve.keyframe_points.insert(frame=range[0], value=0.0).interpolation = interpolation
    fcurve.keyframe_points.insert(frame=range[1], value=0.0).interpolation = interpolation
    return fcurve

def ensure_tracks_for_rig(obj):
    ## This sucks but I can't figure out how else to iterate programmatically.
    base = "data.shirakumo_trial_extra_props"
    ensure_track_for_property(obj, base+".cancelable")
    ensure_track_for_property(obj, base+".invincible")
    ensure_track_for_property(obj, base+".damage_target", "LINEAR")
    ensure_track_for_property(obj, base+".stun_target", "LINEAR")
    ensure_track_for_property(obj, base+".knock_target")
    ensure_track_for_property(obj, base+".lock_target")
    ensure_track_for_property(obj, base+".lock_camera")

def delete_track_for_property(obj, data_path):
    for fcurve in obj.animation_data.action.fcurves:
        if fcurve.data_path == data_path:
            obj.animation_data.action.fcurves.remove(fcurve)
            return

def delete_tracks_for_rig(obj):
    base = "data.shirakumo_trial_extra_props"
    delete_track_for_property(obj, base+".cancelable")
    delete_track_for_property(obj, base+".invincible")
    delete_track_for_property(obj, base+".damage_target")
    delete_track_for_property(obj, base+".stun_target")
    delete_track_for_property(obj, base+".knock_target")
    delete_track_for_property(obj, base+".lock_target")
    delete_track_for_property(obj, base+".lock_camera")

def root_motion_changed(self, context):
    obj = context.object
    if obj.animation_data != None:
        if self.root_motion == True:
            ensure_tracks_for_rig(obj)
        else:
            delete_tracks_for_rig(obj)

class SHIRAKUMO_TRIAL_action_properties(bpy.types.PropertyGroup):
    root_motion: bpy.props.BoolProperty(
        name="Root Motion",
        default=False,
        update=root_motion_changed,
        description="Whether the engine should translate motion on the root bone to physics motion")
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
        col = flow.column()
        col.prop(obj.shirakumo_trial_extra_props, "root_motion")
        col = flow.column()
        col.enabled = obj.shirakumo_trial_extra_props.root_motion
        col.prop(obj.shirakumo_trial_extra_props, "velocity_scale")
        col = flow.column()
        col.prop(obj.shirakumo_trial_extra_props, "loop_animation")
        col = flow.column()
        col.enabled = not obj.shirakumo_trial_extra_props.loop_animation
        col.prop(obj.shirakumo_trial_extra_props, "next_animation")

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
