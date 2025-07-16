import bpy
from . import level
from . import animations
from . import physics
from . import exporter
from . import importer

bl_info = {
    "name": "Shirakumo Trial Extensions",
    "version": (0, 0, 1),
    "blender": (4, 0, 0),
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
    physics,
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

from .exporter import glTF2ExportUserExtension
from .importer import glTF2ImportUserExtension
