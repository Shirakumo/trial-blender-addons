import bpy
from io_scene_gltf2.io.com import gltf2_io

class glTF2ExportUserExtension:
    def __init__(self):
        from io_scene_gltf2.io.com.gltf2_io_extensions import Extension
        self.Extension = Extension
        self.properties = bpy.context.scene.shirakumo_trial_exporter_props

    def gather_gltf_extensions_hook(self, gltf2_plan, export_settings):
        if not self.properties.enabled:
            return

    def gather_scene_hook(self, gltf2_scene, blender_scene, export_settings):
        if not self.properties.enabled:
            return

    def gather_node_hook(self, gltf2_object, blender_object, export_settings):
        if not self.properties.enabled:
            return
        name = "SHIRAKUMO_Trial"
        gltf2_object.extensions[name] = self.Extension(
            name=name,
            required=False,
            extension={})
