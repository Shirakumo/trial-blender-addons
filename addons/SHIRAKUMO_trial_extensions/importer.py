import bpy
from typing import Dict
from io_scene_gltf2.io.com import gltf2_io

class glTF2ImportUserExtension:
    name = "SHIRAKUMO_Trial"

    def __init__(self):
        self.properties = bpy.context.scene.shirakumo_trial_importer_props
