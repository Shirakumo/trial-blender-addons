import bpy
import os
import logging
from math import atan2
from io_scene_gltf2.io.com import gltf2_io

logger = logging.getLogger('glTFImporter')

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
        bpy.context.scene.shirakumo_trial_file_properties.export_path = bpy.path.relpath(export_settings['gltf_filepath'])
        if not self.properties.enabled:
            return
        bg = blender_object.world.node_tree.nodes['Background']
        if bg and bg.inputs and bg.inputs[0].links:
            int = bg.inputs[1].default_value
            tex = bg.inputs[0].links[0].from_node
            img = tex.image
            ori = None
            if 0 < len(tex.inputs[0].links):
                ori = [x for x in tex.inputs[0].links[0].from_socket.default_value]
            path = None
            if img:
                if 0 < len(img.packed_files):
                    origpath = img.filepath
                    path = os.path.join(os.path.dirname(export_settings['gltf_filepath']), os.path.basename(origpath))
                    if os.path.isfile(path):
                        logger.info("Skipping unpacking %s to %s", img.name, path)
                    else:
                        logger.info("Unpacking %s to %s", img.name, path)
                        img.file_format = 'HDR'
                        img.filepath = path
                        img.unpack(method='WRITE_LOCAL')
                        img.pack()
                        img.filepath = origpath
                elif img.filepath:
                    path = img.filepath
                    if path.startswith("//"):
                        path = bpy.path.abspath(path)
            if path:
                if path.startswith("/"):
                    path = os.path.relpath(path, os.path.dirname(export_settings['gltf_filepath']))
                logger.info("Referencing %s with path %s", img.name, path)
                self.add_extension(gltf2_node,
                                   ("envmap", args_dict(
                                       ("file", path),
                                       ("color", [int,int,int], [1.0,1.0,1.0]),
                                       ("orientation", ori))))

    def gather_node_hook(self, gltf2_node, blender_object, export_settings):
        if not self.properties.enabled:
            return
        if isinstance(blender_object, bpy.types.Collection):
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
                                       ("snapToSurface", props.snap_to_surface, True),
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
                                   ("virtual", props.virtual, False),
                                   ("instanceOf", props.instance_of, ""))

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
        fcurves = []
        if hasattr(blender_action, 'layers'):
            fcurves = blender_action.layers[0].strips[0].channelbag(blender_action.slots[0]).fcurves
        else:
            fcurves = blender_action.fcurves
        for fcurve in fcurves:
            if fcurve.data_path.startswith(base):
                name = fcurve.data_path[len(base):]
                extra_tracks[name] = self.encode_fcurve(fcurve, blender_action.frame_range)
        effects = []
        for marker in blender_action.pose_markers:
            if marker.name.startswith("["):
                name = marker.name[1:].strip()
                pair = None
                for marker2 in blender_action.pose_markers:
                    if marker2.name.endswith("]") and marker2.name[:-1].strip() == name:
                        pair = marker2
                        break
                if pair == None:
                    logger.warning("Unmatched open marker pair: "+marker.name)
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
        if props.type == "ADDITIVE":
            self.add_extension(gltf2_animation, ("type", "ADDITIVE"))
        else:
            self.add_extension(gltf2_animation,
                               ("type", props.type, "DEFAULT"),
                               ("velocityScale", props.velocity_scale, 1.0),
                               ("loop", props.loop_animation, True),
                               ("next", props.next_animation, ""),
                               ("blendDuration", props.blend_duration, 0.2),
                               ("extraTracks", extra_tracks),
                               ("effects", effects, []))

def draw_export(context, layout):
    header, body = layout.panel("Shirakumo Trial Extensions", default_closed=False)
    header.use_property_split = False
    props = bpy.context.scene.shirakumo_trial_exporter_props
    header.prop(props, 'enabled')


class SHIRAKUMO_TRIAL_exporter_properties(bpy.types.PropertyGroup):
    enabled: bpy.props.BoolProperty(
        name="Shirakumo Trial Extensions",
        description="Include Trial-specific extensions",
        default=True)

def register():
    bpy.utils.register_class(SHIRAKUMO_TRIAL_exporter_properties)
    bpy.types.Scene.shirakumo_trial_exporter_props = bpy.props.PointerProperty(
        type=SHIRAKUMO_TRIAL_exporter_properties)
    from io_scene_gltf2 import exporter_extension_layout_draw
    exporter_extension_layout_draw['Shirakumo Trial Extensions'] = draw_export

def unregister():
    bpy.utils.unregister_class(SHIRAKUMO_TRIAL_exporter_properties)
    del bpy.types.Scene.shirakumo_trial_exporter_props
    from io_scene_gltf2 import exporter_extension_layout_draw
    del exporter_extension_layout_draw['Shirakumo Trial Extensions']
