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

    def add_extension(self, gltf2_object, *args):
        if gltf2_object.extensions == None:
            gltf2_object.extensions = {}
        
        props = {}
        for (name, val, default) in args:
            if val != default:
                props[name] = val
        
        if props != {}:
            gltf2_object.extensions[self.name] = self.Extension(
                name=self.name,
                required=False,
                extension=props)

    def gather_scene_hook(self, gltf2_node, blender_object, export_settings):
        if not self.properties.enabled:
            return
        bg = blender_object.world.node_tree.nodes['Background']
        if bg:
            intensity = bg.inputs[1].default_value
            texture = bg.inputs[0].links[0].from_node
            orientation = None
            if 0 < len(texture.inputs[0].links):
                orientation = [x for x in texture.inputs[0].links[0].from_socket.default_value]
            if texture.image and texture.image.filepath:
                self.add_extension(gltf2_node,
                                   ("envmap", texture.image.filepath, None),
                                   ("envmapColor", [intensity,intensity,intensity], [1.0,1.0,1.0]),
                                   ("envmapOrientation", orientation, None))
            

    def gather_node_hook(self, gltf2_node, blender_object, export_settings):
        if not self.properties.enabled:
            return
        if blender_object.type == "ARMATURE":
            props = blender_object.data.shirakumo_trial_extra_props
            self.add_extension(gltf2_node,
                               ("cancelable", True, None),
                               ("invincible", False, None),
                               ("targetDamage", 0.0, None),
                               ("stunTarget", 0.0, None),
                               ("knockTarget", False, None),
                               ("lockTarget", False, None),
                               ("lockCamera", False, None))
        elif blender_object.type == "OBJECT":
            props = blender_object.shirakumo_trial_trigger_props
            if props.type == "TRIGGER":
                self.add_extension(gltf2_node,
                                   ("form", props.form, None))
            if props.type == "SPAWNER":
                self.add_extension(gltf2_node,
                                   ("spawn", props.spawn, None),
                                   ("spawnCount", props.spawn_count, 1),
                                   ("autoDeactivate", props.auto_deactivate, True),
                                   ("respawnCooldown", props.respawn_cooldown, 0.0))
            if props.type == "KILLVOLUME":
                self.add_extension(gltf2_node,
                                   ("kill", props.kill_type, None))

    def gather_animation_hook(self, gltf2_animation, blender_action, blender_object, export_settings):
        if not self.properties.enabled:
            return
        props = blender_action.shirakumo_trial_extra_props
        self.add_extension(gltf2_animation,
                           ("rootMotion", props.root_motion, False),
                           ("velocityScale", props.velocity_scale, 1.0),
                           ("loop", props.loop_animation, True),
                           ("next", props.next_animation, ""))


