import bpy
import gpu
import math
from mathutils import Quaternion, Vector, Euler

class SHIRAKUMO_trial_exporter_properties(bpy.types.PropertyGroup):
    enabled: bpy.props.BoolProperty(
        name="SHIRAKUMO_trial_extensions",
        description="Include Trial-specific extensions",
        default=True,
    )

class SHIRAKUMO_trial_importer_properties(bpy.types.PropertyGroup):
    enabled: bpy.props.BoolProperty(
        name="SHIRAKUMO_trial_extensions",
        description="Include Trial-specific extensions",
        default=True,
    )

registered_classes = [
    SHIRAKUMO_trial_exporter_properties,
    SHIRAKUMO_trial_importer_properties,
]

def register():
    for panel in registered_classes:
        bpy.utils.register_class(panel)
    
    bpy.types.Scene.shirakumo_trial_exporter_props = bpy.props.PointerProperty(
        type=SHIRAKUMO_trial_exporter_properties)
    bpy.types.Scene.shirakumo_trial_importer_props = bpy.props.PointerProperty(
        type=SHIRAKUMO_trial_importer_properties)

def unregister():
    for panel in registered_classes:
        bpy.utils.unregister_class(panel)
    del bpy.types.Scene.shirakumo_trial_exporter_props
    del bpy.types.Scene.shirakumo_trial_importer_props
