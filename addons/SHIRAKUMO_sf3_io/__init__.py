import bpy
from bpy_extras.io_utils import poll_file_object_drop
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

class IO_FH_sf3(bpy.types.FileHandler):
    bl_idname = "IO_FH_sf3"
    bl_label = "SF3"
    bl_import_operator = "import_scene.sf3"
    bl_export_operator = "export_scene.sf3"
    bl_file_extensions = ".sf3"

    @classmethod
    def poll_drop(cls, context):
        return poll_file_object_drop(context)


def register():
    bpy.utils.register_class(IO_FH_sf3)
    for mod in modules:
        mod.register()

def unregister():
    bpy.utils.unregister_class(IO_FH_sf3)
    for mod in modules:
        mod.unregister()

if __name__ == "__main__":
    register()
