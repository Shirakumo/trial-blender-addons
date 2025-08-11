import bpy
from bpy_extras import object_utils,view3d_utils
from pathlib import Path
from mathutils import Vector,Matrix

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

def is_physics(obj):
    return (obj and
            hasattr(obj, 'rigid_body') and
            hasattr(obj, 'shirakumo_trial_physics_props') and
            obj.rigid_body)

def is_trigger(obj):
    return (is_physics(obj) and
            obj.shirakumo_trial_physics_props.type in
            ["TRIGGER", "SPAWNER", "KILLVOLUME", "CHECKPOINT", "PROGRESSION", "CAMERA"])

def is_environment(obj):
    return (is_physics(obj) and
            obj.shirakumo_trial_physics_props.type in
            ["ENVIRONMENT"])

def is_prop(obj):
    return (is_physics(obj) and
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

def snap_to_grid(p, grid=0.1, basis=Matrix.Identity(4)):
    if grid == 0.0:
        return p
    p = basis.inverted_safe() @ p
    r = [*p]
    for i in range(len(r)):
        r[i] = round((r[i])/grid)*grid
    return basis @ Vector(r)

def center_in_view(obj=None, context=bpy.context, middle=None):
    region = context.region
    if obj is None:
        obj = context.object
    if middle is None:
        middle = [region.width / 2.0, region.height / 2.0]
    center = view3d_utils.region_2d_to_origin_3d(region, context.space_data.region_3d, middle)
    forward = view3d_utils.region_2d_to_vector_3d(region, context.space_data.region_3d, middle)
    forward.normalize()

    hit, loc, normal, *_ = context.scene.ray_cast(context.view_layer.depsgraph, center, forward)
    if not hit:
        loc = view3d_utils.region_2d_to_location_3d(region, context.space_data.region_3d, middle, Vector())
    while hit:
        if normal @ forward < 0.0:
            break
        center = loc + forward
        hit, loc, normal, *_ = context.scene.ray_cast(context.view_layer.depsgraph, center, forward)
    center = loc - Vector([forward[0] * obj.dimensions[0] * 0.5,
                           forward[1] * obj.dimensions[1] * 0.5,
                           forward[2] * obj.dimensions[2] * 0.5])
    obj.location = snap_to_grid(center)
