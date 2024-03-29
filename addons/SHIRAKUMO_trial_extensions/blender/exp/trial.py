import bpy
from typing import Dict
from io_scene_gltf2.io.com import gltf2_io

def group_as_dict(group: bpy.types.PropertyGroup) -> Dict:
    prop_dict = {}
    for key in group.__annotations__.keys():
        prop_type = group.__annotations__[key].function
        # Pointers to other property groups
        if prop_type == bpy.types.PointerProperty:
            prop_dict[key] = group_as_dict(getattr(group, key))
        # Store collection properties as lists
        elif prop_type == bpy.types.CollectionProperty:
            prop_dict[key] = [group_as_dict(i) for i in getattr(group, key)]
        # Get everything else as a value
        else:
            prop_dict[key] = getattr(group, key)
    return prop_dict

class glTF2ExportUserExtension:
    name = "SHIRAKUMO_Trial"

    def __init__(self):
        from io_scene_gltf2.io.com.gltf2_io_extensions import Extension
        self.Extension = Extension
        self.properties = bpy.context.scene.shirakumo_trial_exporter_props

    def add_extension(self, gltf2_object, data):
        if gltf2_object.extensions == None:
            gltf2_object.extensions = {}
        gltf2_object.extensions[self.name] = self.Extension(
            name=self.name,
            required=False,
            extension=data)

    def gather_node_hook(self, gltf2_node, blender_object, export_settings):
        if not self.properties.enabled:
            return
        if blender_object.type == 'ARMATURE':
            self.add_extension(gltf2_node, group_as_dict(blender_object.data.shirakumo_trial_extra_props))

    def gather_animation_hook(self, gltf2_animation, blender_action, blender_object, export_settings):
        if not self.properties.enabled:
            return
        self.add_extension(gltf2_animation, group_as_dict(blender_action.shirakumo_trial_extra_props))

    def gather_animation_channel_hook(self, gltf2_animation_channel, channel, blender_object, action_name, node_channel_is_animated, export_settings):
        if not self.properties.enabled:
            return
        print(blender_object)

    def gather_animation_channel_target_hook(self, gltf2_animation_channel_target, channels, blender_object, bake_bone, bake_channel, export_settings):
        if not self.properties.enabled:
            return
        print(blender_object)

