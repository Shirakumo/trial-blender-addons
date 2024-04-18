import bpy
import bmesh
from pathlib import Path
from math import sqrt

def push_selection(new):
    previous_selected = []
    for obj in bpy.context.selected_objects:
        previous_selected.append(obj)
        obj.select_set(False)
    for obj in new:
        obj.select_set(True)
    return previous_selected

class Selection(object):
    def __init__(self, new=[]):
        self.previous = []
        self.new = new
        
    def __enter__(self):
        self.previous = push_selection(self.new)
        return self
    
    def __exit__(self, *args):
        push_selection(self.previous)

def hide_all(filter):
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            if filter(obj):
                obj.hide_render = True
            else:
                obj.hide_render = False

def is_bakable_object(obj):
    return (obj.type == 'MESH' and
            (not obj.rigid_body or
             not obj.khr_physics_extra_props or
             not obj.khr_physics_extra_props.is_trigger))

def object_surface_area(obj):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    size = sum(f.calc_area() for f in bm.faces)
    bm.free()
    return size

def ensure_ao_material(obj, size=None, resize=False):
    if not obj.data.materials:
        mat = bpy.data.materials.new(name="AO_Material")
        mat.use_nodes = True
        obj.data.materials.append(mat)

    ao_map_resolution = bpy.context.scene.shirakumo_trial_file_properties.ao_map_resolution
    mat = obj.data.materials[0]
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    if not bsdf.inputs['Base Color'].links:
        if not size:
            size = int(ao_map_resolution*sqrt(object_surface_area(obj)))
        tex = mat.node_tree.nodes.new("ShaderNodeTexImage")
        tex.image = bpy.data.images.new("AO", size, size)
        mat.node_tree.links.new(bsdf.inputs['Base Color'], tex.outputs['Color'])

    img = bsdf.inputs['Base Color'].links[0].from_node.image
    if resize:
        if not size:
            size = int(ao_map_resolution*sqrt(object_surface_area(obj)))
        if img.size[0] != size:
            img.scale(size, size)

def ensure_physics_object(obj):
    if not obj.rigid_body:
        with Selection([obj]) as sel:
            bpy.ops.rigidbody.objects_add()

def rebake_object(obj, resize=True):
    print("Rebake "+obj.name)
    if not obj.rigid_body or obj.khr_physics_extra_props.infinite_mass:
        hide_all(lambda obj : obj.rigid_body and not obj.khr_physics_extra_props.infinite_mass)
    else:
        hide_all(lambda obj : True)
        obj.hide_render = False

    with Selection([obj]) as sel:
        ensure_ao_material(obj, None, resize)
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.smart_project(island_margin=0.001)
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.scene.render.engine = 'CYCLES'
        bpy.ops.object.bake('INVOKE_DEFAULT', type='AO', use_clear=True)

def export_single_object(obj=None, path=None):
    if obj == None:
        obj = bpy.context.selected_objects
    if not type(obj) is list:
        obj = [obj]

    bpy.ops.scene.new(type='EMPTY')
    for o in obj:
        bpy.context.scene.objects.link(o)
        ensure_physics_object(o)
        rebake_object(o)
    bpy.ops.export_scene.gltf(
        filepath=str(path),
        check_existing=False,
        use_active_scene=True)
    bpy.ops.scene.delete()

class SteppedOperator(bpy.types.Operator):
    def __init__(self):
        self.steps = []
        self.index = -1
        self.timer = None
        self.timer_count = 0

    def modal(self, context, event):
        if len(self.steps) <= self.index:
            context.window_manager.event_timer_remove(self.timer)
            context.object.shirakumo_operator_progress = -1.0
            context.area.tag_redraw()
            return {'FINISHED'}

        if event.type == 'TIMER':
            self.timer_count += 1
            if 10 <= self.timer_count and not bpy.app.is_job_running('OBJECT_BAKE'):
                self.timer_count = 0
                self.index += 1
                if self.index < len(self.steps):
                    try:
                        self.steps[self.index]()
                    except:
                        import traceback
                        print(traceback.format_exc())
                        context.window_manager.event_timer_remove(self.timer)
                        context.object.shirakumo_operator_progress = -1.0
                        context.area.tag_redraw()
                        return {'CANCELLED'}
        
        context.object.shirakumo_operator_progress = float(max(0,self.index))/len(self.steps)
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        context.object.shirakumo_operator_progress = 0.0
        context.window_manager.modal_handler_add(self)
        self.timer = context.window_manager.event_timer_add(0.1, window=context.window)
        self.prepare(context, event)
        return {'RUNNING_MODAL'}

class SHIRAKUMO_TRIAL_OT_rebake(SteppedOperator):
    bl_idname = "shirakumo_trial.rebake"
    bl_label = "ReBake"

    @classmethod
    def poll(cls, context):
        return context.object.shirakumo_operator_progress < 0
    
    def prepare(self, context, event):
        objects = context.selected_objects
        if len(objects) == 0:
            objects = bpy.data.objects
        for obj in objects:
            if is_bakable_object(obj):
                self.steps.append(lambda o=obj : rebake_object(o))

class SHIRAKUMO_TRIAL_OT_reexport(SteppedOperator):
    bl_idname = "shirakumo_trial.reexport"
    bl_label = "ReExport"
    
    def prepare(self, context, event):
        path = context.scene.shirakumo_trial_file_properties.export_path
        if path == '' or event.ctrl:
            self.steps.append(lambda : bpy.ops.export_scene.gltf('INVOKE_DEFAULT',
                                                                 check_existing=False,
                                                                 use_visible=True))
        else:
            self.steps.append(lambda : bpy.ops.export_scene.gltf(filepath=path,
                                                                 check_existing=False,
                                                                 use_visible=True))

class SHIRAKUMO_TRIAL_OT_export_as_object(SteppedOperator):
    bl_idname = "shirakumo_trial.export_as_object"
    bl_label = "Export as Object"

    @classmethod
    def poll(cls, context):
        if context.object.shirakumo_operator_progress < 0:
            for obj in context.selected_objects:
                if obj.type == 'MESH':
                    return True
    
    def prepare(self, context, event):
        self.steps.append(lambda : export_single_object())

class SHIRAKUMO_TRIAL_PT_edit_panel(bpy.types.Panel):
    bl_idname = "SHIRAKUMO_TRIAL_PT_edit_panel"
    bl_label = "Trial Extensions"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Edit"
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout
        
        if 0 <= context.object.shirakumo_operator_progress:
            layout.column().progress(text="Working..." , factor=context.object.shirakumo_operator_progress)
        else:
            layout.column().prop(context.scene.shirakumo_trial_file_properties, "ao_map_resolution")
            if 0 < len(context.selected_objects):
                layout.column().operator("shirakumo_trial.rebake", text="ReBake Selected")
            else:
                layout.column().operator("shirakumo_trial.rebake", text="ReBake All")
            layout.column().operator("shirakumo_trial.reexport", text="ReExport")
            layout.column().operator("shirakumo_trial.export_as_object", text="Export as Object")

class SHIRAKUMO_TRIAL_file_properties(bpy.types.PropertyGroup):
    ao_map_resolution: bpy.props.IntProperty(
        name="AO Map Resolution",
        default=16, min=1, soft_max=256, subtype='FACTOR', options=set(),
        description="The resolution scaling for ambient occlusion maps")
    export_path: bpy.props.StringProperty(
        name="Export Path",
        default="", subtype='FILE_PATH', options=set(),
        description="The path to export to with the ReExport button")

registered_classes = [
    SHIRAKUMO_TRIAL_OT_rebake,
    SHIRAKUMO_TRIAL_OT_reexport,
    SHIRAKUMO_TRIAL_OT_export_as_object,
    SHIRAKUMO_TRIAL_PT_edit_panel,
    SHIRAKUMO_TRIAL_file_properties,
]

def register():
    for cls in registered_classes:
        bpy.utils.register_class(cls)
    bpy.types.Object.shirakumo_operator_progress = bpy.props.FloatProperty(name="Progress", default=-1.0)
    bpy.types.Scene.shirakumo_trial_file_properties = bpy.props.PointerProperty(
        type=SHIRAKUMO_TRIAL_file_properties)

def unregister():
    del bpy.types.Object.shirakumo_operator_progress
    del bpy.types.Scene.shirakumo_trial_file_properties
    for cls in registered_classes:
        bpy.utils.unregister_class(cls)
