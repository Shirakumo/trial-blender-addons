import bpy
from typing import Dict
from io_scene_gltf2.io.com import gltf2_io

def args_dict(*args):
    props = {}
    for arg in args:
        if len(arg) == 2:
            if arg[1] != None:
                props[arg[0]] = arg[1]
        elif len(arg) == 3:
            if arg[1] != arg[2]:
                props[arg[0]] = arg[1]
    return props

class glTF2ExportUserExtension:
    name = "SHIRAKUMO_Trial"

    def __init__(self):
        from io_scene_gltf2.io.com.gltf2_io_extensions import Extension
        self.Extension = Extension
        self.properties = bpy.context.scene.shirakumo_trial_exporter_props

    def add_extension(self, gltf2_object, *args):
        if gltf2_object.extensions == None:
            gltf2_object.extensions = {}
        
        props = args_dict(*args)
        if props != {}:
            gltf2_object.extensions[self.name] = self.Extension(
                name=self.name,
                required=False,
                extension=props)

    def gather_scene_hook(self, gltf2_node, blender_object, export_settings):
        if not self.properties.enabled:
            return
        bg = blender_object.world.node_tree.nodes['Background']
        if bg and bg.inputs and bg.inputs[0].links:
            int = bg.inputs[1].default_value
            tex = bg.inputs[0].links[0].from_node
            ori = None
            if 0 < len(tex.inputs[0].links):
                ori = [x for x in tex.inputs[0].links[0].from_socket.default_value]
            if tex.image and tex.image.filepath:
                self.add_extension(gltf2_node,
                                   ("envmap", tex.image.filepath),
                                   ("envmapColor", [int,int,int], [1.0,1.0,1.0]),
                                   ("envmapOrientation", ori))
            

    def gather_node_hook(self, gltf2_node, blender_object, export_settings):
        if not self.properties.enabled:
            return
        if blender_object.type == "ARMATURE":
            props = blender_object.data.shirakumo_trial_extra_props
            self.add_extension(gltf2_node,
                               ("cancelable", True),
                               ("invincible", False),
                               ("targetDamage", 0.0),
                               ("stunTarget", 0.0),
                               ("knockTarget", False),
                               ("lockTarget", False),
                               ("lockCamera", False))
        elif blender_object.type == "OBJECT":
            props = blender_object.shirakumo_trial_trigger_props
            if props.type == "TRIGGER":
                self.add_extension(gltf2_node,
                                   ("trigger", args_dict(
                                       ("form", props.form))))
            if props.type == "SPAWNER":
                self.add_extension(gltf2_node,
                                   ("spawner", args_dict(
                                       ("spawn", props.spawn),
                                       ("spawnCount", props.spawn_count, 1),
                                       ("autoDeactivate", props.auto_deactivate, True),
                                       ("respawnCooldown", props.respawn_cooldown, 0.0))))
            if props.type == "KILLVOLUME":
                self.add_extension(gltf2_node,
                                   ("killvolume", args_dict(
                                       ("kill", props.kill_type))))

    def gather_animation_hook(self, gltf2_animation, blender_action, blender_object, export_settings):
        if not self.properties.enabled:
            return
        props = blender_action.shirakumo_trial_extra_props
        self.add_extension(gltf2_animation,
                           ("rootMotion", props.root_motion, False),
                           ("velocityScale", props.velocity_scale, 1.0),
                           ("loop", props.loop_animation, True),
                           ("next", props.next_animation, ""))


