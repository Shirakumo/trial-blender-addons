import bpy
from pathlib import Path

def message_box(message="", title="Trial", icon='INFO'):
    def draw(self, context):
        self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)

def push_selection(new):
    previous_selected = []
    for obj in bpy.context.selected_objects:
        previous_selected.append(obj)
        obj.select_set(False)
    for obj in new:
        obj.select_set(True)
    return previous_selected

class ObjectMode(object):
    def __init__(self, new=None):
        self.previous = None
        self.new = new

    def __enter__(self):
        self.previous = bpy.context.object.mode
        bpy.ops.object.mode_set(mode=self.new)
        return self

    def __exit__(self ,*args):
        bpy.ops.object.mode_set(mode=self.previous)

class Selection(object):
    def __init__(self, new=[]):
        self.previous = []
        self.new = new
        
    def __enter__(self):
        self.previous = push_selection(self.new)
        return self
    
    def __exit__(self, *args):
        push_selection(self.previous)

def unique_meshes(objects):
    cache = {}
    for obj in objects:
        if obj.data not in cache:
            cache[obj.data] = obj
    return cache.values()

def hide_all(filter):
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            if filter(obj):
                obj.hide_render = True
            else:
                obj.hide_render = False

def clear_children(obj):
    for child in obj.children:
        clear_children(child)
        bpy.data.objects.remove(child, do_unlink=True)
    return obj

def is_trigger(obj):
    return (obj.shirakumo_trial_physics_props and
            obj.shirakumo_trial_physics_props.type in
            ["TRIGGER", "SPAWNER", "KILLVOLUME", "CHECKPOINT", "PROGRESSION", "CAMERA"])

def is_environment(obj):
    return (obj.shirakumo_trial_physics_props and
            obj.shirakumo_trial_physics_props.type in
            ["ENVIRONMENT"])

def is_prop(obj):
    return (obj.shirakumo_trial_physics_props and
            obj.shirakumo_trial_physics_props.type in
            ["PROP"])

def ensure_physics_object(obj, type='NONE'):
    if not obj.rigid_body:
        with Selection([obj]) as sel:
            bpy.ops.rigidbody.objects_add()
    obj.shirakumo_trial_physics_props.type = type

def find_asset(name, kind, library=None):
    if library is None:
        for library in bpy.context.preferences.filepaths.asset_libraries:
            asset = find_asset(name, kind, library)
            if asset is not None:
                return asset
    elif isinstance(library, bpy.types.UserAssetLibrary):
        library_name = library.name
        library_path = Path(library.path)
        for blend_file in library_path.glob("**/*.blend"):
            if blend_file.is_file():
                asset = find_asset(name, kind, blend_file)
                if asset is not None:
                    return asset
    elif isinstance(library, Path):
        with bpy.data.libraries.load(str(library), assets_only=True) as (data_from, data_to):
            setattr(data_to, kind, [n for n in getattr(data_from, kind) if n == name])
        for obj in getattr(data_to, kind):
            return obj
    else:
        raise Exception("Unknown library type: "+str(type(library)))
    return None
