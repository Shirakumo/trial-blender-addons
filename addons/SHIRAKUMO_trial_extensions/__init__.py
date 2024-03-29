import bpy
from .blender.com import trial_ui
from .blender.exp.trial import glTF2ExportUserExtension

bl_info = {
    "name": "SHIRAKUMO_trial_extensions",
    "version": (0, 0, 1),
    "blender": (3, 6, 0),
    "isDraft": True,
    "developer": "Yukari Hafner",
    "category": "Import-Export",
    "location": "File > Export > glTF 2.0",
    "description": "Extension for Trial game engine extensions to glTF files",
    "tracker_url": "https://github.com/shirakumo/trial-blender-addons/issues",
    "url": "https://github.com/shirakumo/trial-blender-addons",
}

def register():
    trial_ui.register()

def unregister():
    unregister_panel()
    trial_ui.unregister()

def register_panel():
    try:
        bpy.utils.register_class(GLTF_PT_SHIRAKUMO_Trial_ImportExtensionPanel)
        bpy.utils.register_class(GLTF_PT_SHIRAKUMO_Trial_ExportExtensionPanel)
    except Exception:
        pass
    return unregister_panel

def unregister_panel():
    for p in (GLTF_PT_SHIRAKUMO_Trial_ExportExtensionPanel,
              GLTF_PT_SHIRAKUMO_Trial_ImportExtensionPanel):
        try:
            bpy.utils.unregister_class(p)
        except Exception:
            pass

class GLTF_PT_SHIRAKUMO_Trial_ExportExtensionPanel(bpy.types.Panel):
    bl_space_type = "FILE_BROWSER"
    bl_region_type = "TOOL_PROPS"
    bl_label = "Enabled"
    bl_parent_id = "GLTF_PT_export_user_extensions"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator
        return operator.bl_idname == "EXPORT_SCENE_OT_gltf"

    def draw_header(self, context):
        props = bpy.context.scene.shirakumo_trial_exporter_props
        self.layout.prop(props, "enabled")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        props = bpy.context.scene.shirakumo_trial_exporter_props
        layout.active = props.enabled

class GLTF_PT_SHIRAKUMO_Trial_ImportExtensionPanel(bpy.types.Panel):
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
