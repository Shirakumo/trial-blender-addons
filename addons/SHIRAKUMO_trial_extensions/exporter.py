import bpy
import os
from math import atan2
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
    name = "SHIRAKUMO_trial"
    ## KLUDGE: hard-coding 60 FPS
    framerate = 60

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
        bpy.context.scene.shirakumo_trial_file_properties.export_path = export_settings['gltf_filepath']
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
                path = tex.image.filepath
                if path.startswith("//"):
                    path = bpy.path.abspath(path)
                if path.startswith("/"):
                    path = os.path.relpath(path, os.path.dirname(export_settings['gltf_filepath']))
                self.add_extension(gltf2_node,
                                   ("envmap", path),
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
        elif blender_object.type == "MESH":
            props = blender_object.shirakumo_trial_physics_props
            if props.type == "TRIGGER":
                self.add_extension(gltf2_node,
                                   ("trigger", args_dict(
                                       ("filter", props.filter, "T"),
                                       ("form", props.form))))
            elif props.type == "SPAWNER":
                self.add_extension(gltf2_node,
                                   ("spawner", args_dict(
                                       ("filter", props.filter, "T"),
                                       ("spawn", props.spawn),
                                       ("spawnCount", props.spawn_count, 1),
                                       ("autoDeactivate", props.auto_deactivate, True),
                                       ("respawnCooldown", props.respawn_cooldown, 0.0))))
            elif props.type == "KILLVOLUME":
                self.add_extension(gltf2_node,
                                   ("killvolume", args_dict(
                                       ("filter", props.filter, "T"),
                                       ("kill", props.kill_type))))
            elif props.type == "CHECKPOINT":
                spawnpoint = [0,0,0]
                if 0 < len(blender_object.children) and blender_object.children[0]:
                    spawnpoint = list(blender_object.children[0].matrix_local.translation)
                self.add_extension(gltf2_node,
                                   ("checkpoint", args_dict(
                                       ("filter", props.filter, "T"),
                                       ("spawnPoint", spawnpoint, [0,0,0]))))
            elif props.type == "PROGRESSION":
                self.add_extension(gltf2_node,
                                   ("progressionTrigger", args_dict(
                                       ("filter", props.filter, "T"),
                                       ("state", props.state, "progression"),
                                       ("value", props.value, 1.0),
                                       ("mode", props.mode, "INC"),
                                       ("condition", props.condition, "T"))))
            elif props.type == "CAMERA":
                pivot = [0,0,0]
                if 0 < len(blender_object.children) and blender_object.children[0]:
                    pivot = blender_object.children[0]
                    pivot = [pivot.scale[0],
                             pivot.rotation_euler[2],
                             atan2(pivot.location[2], pivot.scale[0])]
                self.add_extension(gltf2_node,
                                   ("cameraTrigger", args_dict(
                                       ("state", props.camera_state),
                                       ("target", props.target, ""),
                                       ("offset", pivot, [0,0,0]))))
            elif props.type == "INTERACTABLE":
                self.add_extension(gltf2_node,
                                   ("interactable", args_dict(
                                       ("interaction", props.interaction),
                                       ("form", props.form),
                                       ("kind", props.interaction_kind))))
            else:
                self.add_extension(gltf2_node,
                                   ("virtual", props.virtual, False))

    def encode_fcurve(self, fcurve, range):
        data = {"interpolation": "CONSTANT",
                "times": [],
                "values": []}
        if fcurve.keyframe_points[0].co[0] != range[0]:
            data["times"].append(float(range[0]) / self.framerate)
            data["values"].append(float(fcurve.keyframe_points[0].co[1]))
        for point in fcurve.keyframe_points:
            data["interpolation"] = point.interpolation
            data["times"].append(float(point.co[0]) / 60.0)
            data["values"].append(float(point.co[1]))
        if fcurve.keyframe_points[-1].co[0] != range[1]:
            data["times"].append(float(range[1]) / 60.0)
            data["values"].append(float(fcurve.keyframe_points[-1].co[1]))
        return data

    def gather_animation_hook(self, gltf2_animation, blender_action, blender_object, export_settings):
        if not self.properties.enabled:
            return
        ## KLUDGE: Ideally we shouldn't do it like this and instead use the proper
        ##         glTF animations channels, but I have no idea how to hook into that
        ##         so....
        extra_tracks = {}
        base = "data.shirakumo_trial_extra_props."
        for fcurve in blender_action.fcurves:
            if fcurve.data_path.startswith(base):
                name = fcurve.data_path[len(base):]
                extra_tracks[name] = self.encode_fcurve(fcurve, blender_action.frame_range)
        effects = []
        for marker in blender_action.pose_markers:
            if marker.name.startswith("["):
                name = marker.name[1:].strip()
                pair = None
                for marker in blender_action.pose_markers:
                    if marker.name.endswith("]") and marker.name[:-1].strip() == name:
                        pair = marker
                        break
                if pair == None:
                    print("Unmatched open marker pair: "+marker.name)
                else:
                    effects.append({
                        "start": float(marker.frame) / self.framerate,
                        "end": float(pair.frame) / self.framerate,
                        "effect": name})
            elif marker.name.endswith("]"):
                pass
            else:
                effects.append({
                    "start": float(marker.frame) / self.framerate,
                    "effect": marker.name})
        
        props = blender_action.shirakumo_trial_extra_props
        self.add_extension(gltf2_animation,
                           ("type", props.type, "DEFAULT"),
                           ("velocityScale", props.velocity_scale, 1.0),
                           ("loop", props.loop_animation, True),
                           ("next", props.next_animation, ""),
                           ("blendDuration", props.blend_duration, 0.2),
                           ("extraTracks", extra_tracks),
                           ("effects", effects, []))

class SHIRAKUMO_TRIAL_exporter_properties(bpy.types.PropertyGroup):
    enabled: bpy.props.BoolProperty(
        name="SHIRAKUMO_TRIAL_extensions",
        description="Include Trial-specific extensions",
        default=True)

def register():
    bpy.utils.register_class(SHIRAKUMO_TRIAL_exporter_properties)
    bpy.types.Scene.shirakumo_trial_exporter_props = bpy.props.PointerProperty(
        type=SHIRAKUMO_TRIAL_exporter_properties)

def unregister():
    bpy.utils.unregister_class(SHIRAKUMO_TRIAL_exporter_properties)
    del bpy.types.Scene.shirakumo_trial_exporter_props
