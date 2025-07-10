import bpy
from . import tools

bl_info = {
    "name": "Rectangle Tools",
    "version": (0, 0, 1),
    "blender": (4, 0, 0),
    "isDraft": True,
    "developer": "Yukari Hafner",
    "category": "",
    "location": "Edit > Tools",
    "description": "Tools to more easily draw rectangles in edit mode",
    "tracker_url": "https://github.com/shirakumo/trial-blender-addons/issues",
    "url": "https://github.com/shirakumo/trial-blender-addons",
}

def register():
    tools.register()

def unregister():
    tools.unregister()
    
if __name__ == "__main__":
    register()
