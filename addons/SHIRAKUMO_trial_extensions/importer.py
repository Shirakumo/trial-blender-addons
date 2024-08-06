import bpy
from typing import Dict
from io_scene_gltf2.io.com import gltf2_io

class glTF2ImportUserExtension:
    name = "SHIRAKUMO_Trial"

    def __init__(self):
        self.properties = bpy.context.scene.shirakumo_trial_importer_props

class SHIRAKUMO_TRIAL_importer_properties(bpy.types.PropertyGroup):
    enabled: bpy.props.BoolProperty(
        name="SHIRAKUMO_TRIAL_extensions",
        description="Include Trial-specific extensions",
        default=True)

def register():
    bpy.utils.register_class(SHIRAKUMO_TRIAL_importer_properties)
    bpy.types.Scene.shirakumo_trial_importer_props = bpy.props.PointerProperty(
        type=SHIRAKUMO_TRIAL_importer_properties)

def unregister():
    bpy.utils.unregister_class(SHIRAKUMO_TRIAL_importer_properties)
    del bpy.types.Scene.shirakumo_trial_importer_props
