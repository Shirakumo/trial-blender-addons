import bpy
import gpu
import math
from mathutils import Quaternion, Vector, Euler

class SHIRAKUMO_trial_exporter_properties(bpy.types.PropertyGroup):
    enabled: bpy.props.BoolProperty(
        name="SHIRAKUMO_trial_extensions",
        description="Include Trial-specific extensions",
        default=True)

class SHIRAKUMO_trial_importer_properties(bpy.types.PropertyGroup):
    enabled: bpy.props.BoolProperty(
        name="SHIRAKUMO_trial_extensions",
        description="Include Trial-specific extensions",
        default=True)

def ensure_track_for_property(obj, data_path, interpolation="CONSTANT"):
    for fcurve in obj.animation_data.action.fcurves:
        if fcurve.data_path == data_path:
            return fcurve
    fcurve = obj.animation_data.action.fcurves.new(data_path)
    keyframe = fcurve.keyframe_points.insert(frame=0.0, value=0.0)
    keyframe.interpolation = interpolation
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

def root_motion_changed(self, context):
    if context.object.animation_data != None and self.root_motion == True:
        ensure_tracks_for_rig(context.object)

class SHIRAKUMO_trial_action_properties(bpy.types.PropertyGroup):
    root_motion: bpy.props.BoolProperty(name="Root Motion", default=False, update=root_motion_changed)
    velocity_scale: bpy.props.FloatProperty(name="Velocity Scale", default=1.0, min=0)
    loop_animation: bpy.props.BoolProperty(name="Loop Animation", default=True)
    next_animation: bpy.props.StringProperty(name="Next Animation", default="")

class SHIRAKUMO_trial_armature_properties(bpy.types.PropertyGroup):
    cancelable: bpy.props.BoolProperty(name="Cancelable", default=True, options={'ANIMATABLE'})
    invincible: bpy.props.BoolProperty(name="Invincible", default=False, options={'ANIMATABLE'})
    damage_target: bpy.props.FloatProperty(name="Target Damage", default=0.0, min=0, options={'ANIMATABLE'})
    stun_target: bpy.props.FloatProperty(name="Target Stun", default=0.0, min=0, options={'ANIMATABLE'})
    knock_target: bpy.props.BoolProperty(name="Target Knockback", default=False, options={'ANIMATABLE'})
    lock_target: bpy.props.BoolProperty(name="Lock Target", default=False, options={'ANIMATABLE'})
    lock_camera: bpy.props.BoolProperty(name="Lock Camera", default=False, options={'ANIMATABLE'})

class SHIRAKUMO_PT_trial_action_panel(bpy.types.Panel):
    bl_idname = "SHIRAKUMO_PT_trial_animation_panel"
    bl_label = "Trial Extensions"
    bl_space_type = "NLA_EDITOR"
    bl_region_type = "UI"
    bl_context = "animation"
    def draw(self, context):
        if context.object.animation_data == None:
            return
        layout = self.layout
        layout.use_property_split = True
        flow = layout.grid_flow(row_major=True, columns=0, even_columns=True, even_rows=False, align=True)
        obj = context.object.animation_data.action
        flow.column().prop(obj.shirakumo_trial_extra_props, "loop_animation")
        flow.column().prop(obj.shirakumo_trial_extra_props, "root_motion")
        flow.column().prop(obj.shirakumo_trial_extra_props, "velocity_scale")
        flow.column().prop(obj.shirakumo_trial_extra_props, "next_animation")

registered_classes = [
    SHIRAKUMO_trial_exporter_properties,
    SHIRAKUMO_trial_importer_properties,
    SHIRAKUMO_trial_action_properties,
    SHIRAKUMO_trial_armature_properties,
    SHIRAKUMO_PT_trial_action_panel,
]

def register():
    for cls in registered_classes:
        bpy.utils.register_class(cls)
    bpy.types.Action.shirakumo_trial_extra_props = bpy.props.PointerProperty(
        type=SHIRAKUMO_trial_action_properties)
    bpy.types.Armature.shirakumo_trial_extra_props = bpy.props.PointerProperty(
        type=SHIRAKUMO_trial_armature_properties)
    bpy.types.Scene.shirakumo_trial_exporter_props = bpy.props.PointerProperty(
        type=SHIRAKUMO_trial_exporter_properties)
    bpy.types.Scene.shirakumo_trial_importer_props = bpy.props.PointerProperty(
        type=SHIRAKUMO_trial_importer_properties)

def unregister():
    for cls in registered_classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Action.shirakumo_trial_extra_props
    del bpy.types.Armature.shirakumo_trial_extra_props
    del bpy.types.Scene.shirakumo_trial_exporter_props
    del bpy.types.Scene.shirakumo_trial_importer_props
