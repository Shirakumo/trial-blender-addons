import bpy
import bmesh
from pathlib import Path

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
            obj.hide_render = filter(obj)

def is_bakable_obj(obj):
    return (obj.type == 'MESH' and
            (not obj.khr_physics_extra_props or
             not obj.khr_physics_extra_props.is_trigger))

def object_surface_area(obj):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    size = sum(f.calc_area() for f in bm.faces)
    bm.free()
    return size

def ensure_ao_material(obj, size=None):
    if not size:
        size = int(100*sqrt(object_surface_area(obj)))

    if not obj.data.materials:
        mat = bpy.data.materials.new(name="AO_Material")
        mat.use_nodes = True
        obj.data.materials.append(ma)
    
    mat = obj.data.materials[0]
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    if not bsdf.inputs['Base Color']:
        tex = bpy.data.textures.new("AO", type='IMAGE')
        tex.image = bpy.data.images.new("AO", size, size)
        mat.texture_slots.add().texture = tex
        mat.node_tree.links.new(bsdf.inputs['Base Color'], tex.outputs['Color'])

def ensure_physics_obj(obj):
    if not obj.rigid_body:
        with Selection([obj]) as sel:
            bpy.ops.rigidbody.objects_add()

def rebake(obj):
    print("Rebake "+str(obj))
    if obj.khr_physics_extra_props.infinite_mass:
        hide_all(lambda obj : not obj.khr_physics_extra_props.infinite_mass)
    else:
        hide_all(lambda obj : True)
        obj.hide_render = False

    with Selection([obj]) as sel:
        ensure_ao_material(obj)
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.smart_project(island_margin=0.001)
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.bake('INVOKE_DEFAULT', type='AO', use_clear=True)

def export_single_object(obj):
    ensure_physics_obj(obj)
    rebake(obj)
    # Create a virtual scene to export the single object
    bpy.ops.scene.new(type='EMPTY')
    bpy.context.scene.objects.link(obj)
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
                    self.steps[self.index]()
        
        context.object.shirakumo_operator_progress = float(max(0,self.index))/len(self.steps)
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        context.object.shirakumo_operator_progress = 0.0
        context.window_manager.modal_handler_add(self)
        self.timer = context.window_manager.event_timer_add(0.1, window=context.window)
        self.prepare(context)
        return {'RUNNING_MODAL'}

class SHIRAKUMO_TRIAL_OT_rebake(SteppedOperator):
    bl_idname = "shirakumo_trial.rebake"
    bl_label = "ReBake Selected"

    @classmethod
    def poll(cls, context):
        if 0 <= context.object.shirakumo_operator_progress: return None
        for obj in context.selected_objects:
            if is_bakable_obj(obj):
                return True
        return None
    
    def prepare(self, context):
        for obj in context.selected_objects:
            if is_bakable_object(obj):
                self.steps.append(lambda : rebake(obj))

class SHIRAKUMO_TRIAL_OT_rebake_all(SteppedOperator):
    bl_idname = "shirakumo_trial.rebake_all"
    bl_label = "ReBake Selected"
    
    @classmethod
    def poll(cls, context):
        if context.object.shirakumo_operator_progress < 0: return True
    
    def prepare(self, context):
        for obj in bpy.data.objects:
            if is_bakable_object(obj):
                self.steps.append(lambda : rebake(obj))

class SHIRAKUMO_TRIAL_OT_reexport(SteppedOperator):
    bl_idname = "shirakumo_trial.reexport"
    bl_label = "ReExport"
    
    def prepare(self, context):
        path = Path(bpy.data.filepath).with_suffix('.glb')
        self.steps.append(lambda : bpy.ops.export_scene.gltf(
            filepath=str(path),
            check_existing=False))

class SHIRAKUMO_TRIAL_PT_bake_panel(bpy.types.Panel):
    bl_idname = "SHIRAKUMO_TRIAL_PT_bake_panel"
    bl_label = "Rebake"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Edit"
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout
        
        if 0 <= context.object.shirakumo_operator_progress:
            layout.progress(factor=context.object.shirakumo_operator_progress)
        else:
            layout.column().operator("shirakumo_trial.rebake", text="ReBake Selected")
            layout.column().operator("shirakumo_trial.rebake_all", text="ReBake All")
            layout.column().operator("shirakumo_trial.reexport", text="ReExport")

registered_classes = [
    SHIRAKUMO_TRIAL_OT_rebake,
    SHIRAKUMO_TRIAL_OT_rebake_all,
    SHIRAKUMO_TRIAL_OT_reexport,
    SHIRAKUMO_TRIAL_PT_bake_panel,
]

def register():
    bpy.types.Object.shirakumo_operator_progress = bpy.props.FloatProperty(name="Progress", default=-1.0)
    for cls in registered_classes:
        bpy.utils.register_class(cls)

def unregister():
    del bpy.types.Object.shirakumo_operator_progress
    for cls in registered_classes:
        bpy.utils.unregister_class(cls)
