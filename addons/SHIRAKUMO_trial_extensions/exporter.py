import bpy
import os
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
    name = "SHIRAKUMO_trial"

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
                    path = tex.image.filepath[2:]
                if path.startswith("/"):
                    path = os.path.relpath(path, export_settings['gltf_filepath'])
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
                spawnpoint = blender_object.children[0]
                if not spawnpoint: return
                self.add_extension(gltf2_node,
                                   ("checkpoint", args_dict(
                                       ("filter", props.filter, "T"),
                                       ("spawnPoint", list(spawnpoint.location)))))
            else:
                self.add_extension(gltf2_node,
                                   ("virtual", props.virtual, False))

    def gather_animation_hook(self, gltf2_animation, blender_action, blender_object, export_settings):
        if not self.properties.enabled:
            return
        props = blender_action.shirakumo_trial_extra_props
        self.add_extension(gltf2_animation,
                           ("rootMotion", props.root_motion, False),
                           ("velocityScale", props.velocity_scale, 1.0),
                           ("loop", props.loop_animation, True),
                           ("next", props.next_animation, ""),
                           ("blendDuration", props.blend_duration, 0.2))

class SHIRAKUMO_TRIAL_exporter_properties(bpy.types.PropertyGroup):
    enabled: bpy.props.BoolProperty(
        name="SHIRAKUMO_TRIAL_extensions",
        description="Include Trial-specific extensions",
        default=True)

class GLTF_PT_SHIRAKUMO_TRIAL_ExportExtensionPanel(bpy.types.Panel):
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

def register():
    try:
        bpy.utils.register_class(GLTF_PT_SHIRAKUMO_TRIAL_ExportExtensionPanel)
        bpy.utils.register_class(SHIRAKUMO_TRIAL_exporter_properties)
        bpy.types.Scene.shirakumo_trial_exporter_props = bpy.props.PointerProperty(
            type=SHIRAKUMO_TRIAL_exporter_properties)
    except:
        pass

def unregister():
    try:
        bpy.utils.unregister_class(GLTF_PT_SHIRAKUMO_TRIAL_ExportExtensionPanel)
        bpy.utils.unregister_class(SHIRAKUMO_TRIAL_exporter_properties)
        del bpy.types.Scene.shirakumo_trial_exporter_props
    except:
        pass
