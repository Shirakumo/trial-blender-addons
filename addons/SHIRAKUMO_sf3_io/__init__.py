import bpy
from . import exporter
from . import importer

bl_info = {
    "name": "SHIRAKUMO_sf3_io",
    "version": (0, 0, 1),
    "blender": (4, 2, 0),
    "isDraft": True,
    "developer": "Yukari Hafner",
    "category": "Import-Export",
    "location": "File > Export > SF3",
    "description": "Export/Import support for Simple File Format Family (SF3) files.",
    "tracker_url": "https://shirakumo.org/projects/trial-blender-addons",
    "url": "https://shirakumo.org/projects/trial-blender-addons",
}

modules = [
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
