import bpy
from . import level
from . import animations
from . import triggers
from . import exporter
from . import importer
from .exporter import glTF2ExportUserExtension
from .importer import glTF2ImportUserExtension

bl_info = {
    "name": "SHIRAKUMO_trial_extensions",
    "version": (0, 0, 1),
    "blender": (3, 6, 0),
    "isDraft": True,
    "developer": "Yukari Hafner",
    "category": "Import-Export",
    "location": "File > Export > glTF 2.0",
    "description": "Addon for Trial game engine extensions",
    "tracker_url": "https://github.com/shirakumo/trial-blender-addons/issues",
    "url": "https://github.com/shirakumo/trial-blender-addons",
}

modules = [
    level,
    animations,
    triggers,
    exporter,
    importer
]

def register():
    for mod in modules:
        mod.register()

def unregister():
    for mod in modules:
        mod.unregister()

if __name__ == "__main__":
    register()
