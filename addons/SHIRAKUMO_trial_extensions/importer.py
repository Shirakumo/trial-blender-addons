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

class GLTF_PT_SHIRAKUMO_TRIAL_ImportExtensionPanel(bpy.types.Panel):
    bl_space_type = "FILE_BROWSER"
    bl_region_type = "TOOL_PROPS"
    bl_label = "Enabled"
    bl_parent_id = "GLTF_PT_import_user_extensions"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator
        return operator.bl_idname == "IMPORT_SCENE_OT_gltf"

    def draw_header(self, context):
        props = bpy.context.scene.shirakumo_trial_importer_props
        self.layout.prop(props, "enabled")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = False
        layout.use_property_decorate = False  # No animation.

        props = bpy.context.scene.shirakumo_trial_importer_props
        layout.active = props.enabled

def register():
    try:
        bpy.utils.register_class(GLTF_PT_SHIRAKUMO_TRIAL_ImportExtensionPanel)
        bpy.utils.register_class(SHIRAKUMO_TRIAL_importer_properties)
        bpy.types.Scene.shirakumo_trial_importer_props = bpy.props.PointerProperty(
            type=SHIRAKUMO_TRIAL_importer_properties)
    except:
        pass

def unregister():
    try:
        bpy.utils.unregister_class(GLTF_PT_SHIRAKUMO_TRIAL_ImportExtensionPanel)
        bpy.utils.unregister_class(SHIRAKUMO_TRIAL_importer_properties)
        del bpy.types.Scene.shirakumo_trial_importer_props
    except:
        pass
