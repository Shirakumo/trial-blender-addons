import bpy
import bmesh
from pathlib import Path
from math import sqrt

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
             obj.shirakumo_trial_physics_props.type in ['NONE', 'INTERACTABLE']))

def object_surface_area(obj):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    size = sum(f.calc_area() for f in bm.faces)
    bm.free()
    return size

def ao_size(obj, size=None):
    if not size:
        ao_map_resolution = bpy.context.scene.shirakumo_trial_file_properties.ao_map_resolution
        size = int(ao_map_resolution*sqrt(object_surface_area(obj)))
    print("AO Size for "+obj.name+": "+str(size))
    if 10000 < size:
        message_box("Clamping AO map size down from "+str(size)+" to 10'000!", "Warning", 'ERROR')
        print("!! Clamping size to 10'000")
        size = 10000
    return size

def ensure_ao_material(obj, size=None, resize=True):
    if not obj.data.materials:
        mat = bpy.data.materials.new(name="AO_Material")
        mat.use_nodes = True
        obj.data.materials.append(mat)

    mat = obj.data.materials[0]
    glTF = mat.node_tree.nodes.get('Group')
    if glTF == None:
        bpy.context.preferences.addons['io_scene_gltf2'].preferences.settings_node_ui = True
        original_type = bpy.context.area.type
        bpy.context.area.type = 'NODE_EDITOR'
        bpy.context.area.spaces.active.node_tree = mat.node_tree
        bpy.ops.node.gltf_settings_node_operator('INVOKE_DEFAULT')
        bpy.context.area.type = original_type
        glTF = mat.node_tree.nodes.get('Group')
    if not glTF.inputs['Occlusion'].links:
        size = ao_size(obj, size)
        tex = mat.node_tree.nodes.new("ShaderNodeTexImage")
        tex.image = bpy.data.images.new("AO", size, size)
        mat.node_tree.links.new(glTF.inputs['Occlusion'], tex.outputs['Color'])

    tex = glTF.inputs['Occlusion'].links[0].from_node

    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    if not bsdf.inputs['Base Color'].links:
        mat.node_tree.links.new(bsdf.inputs['Base Color'], tex.outputs['Color'])

    if resize:
        size = ao_size(obj, size)
        if tex.image.size[0] != size:
            tex.image.scale(size, size)
    return size

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
        size = ensure_ao_material(obj, None, resize)
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.smart_project(island_margin=1/size)
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
        if len(self.steps) <= self.index or len(self.steps) == 0:
            context.window_manager.event_timer_remove(self.timer)
            context.object.shirakumo_operator_progress = -1.0
            if context.area != None:
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
                        if context.area != None:
                            context.area.tag_redraw()
                        return {'CANCELLED'}
        
        context.object.shirakumo_operator_progress = float(max(0,self.index))/len(self.steps)
        if context.area != None:
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
        args = {"check_existing": False,
                "use_visible": True,
                "export_lights": True,
                "export_cameras": True,
                "export_def_bones": True}
        if path == '' or event.ctrl:
            self.steps.append(lambda : bpy.ops.export_scene.gltf('INVOKE_DEFAULT', **args))
        else:
            self.steps.append(lambda : bpy.ops.export_scene.gltf(filepath=path, **args))

class SHIRAKUMO_TRIAL_OT_make_level(bpy.types.Operator):
    bl_idname = "shirakumo_trial.make_level"
    bl_label = "Mark as Level Geo"
    
    def invoke(self, context, event):
        objects = context.selected_objects
        if len(objects) == 0:
            objects = bpy.data.objects
        objects = [ x for x in objects if x.type == 'MESH' ]
        push_selection(objects)
        bpy.ops.object.make_single_user(object=True, obdata=True)
        bpy.ops.object.transform_apply(scale=True)
        bpy.ops.object.join()
        objects = [bpy.context.active_object]
        with ObjectMode('EDIT'):
            bpy.ops.mesh.select_mode(type = 'VERT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.remove_doubles(threshold=0.0001)
            bpy.ops.mesh.select_all(action='DESELECT')
            # bpy.ops.mesh.select_mode(type = 'FACE')
            # bpy.ops.mesh.select_interior_faces()
            # bpy.ops.mesh.delete(type='FACE')
        for obj in objects:
            ensure_physics_object(obj)
            obj.rigid_body.collision_shape = 'MESH'
            obj.khr_physics_extra_props.infinite_mass = True
        return {'FINISHED'}

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

        if not hasattr(context.object, 'shirakumo_operator_progress'):
            pass
        elif 0 <= context.object.shirakumo_operator_progress:
            layout.column().progress(text="Working..." , factor=context.object.shirakumo_operator_progress)
        else:
            layout.column().prop(context.scene.shirakumo_trial_file_properties, "ao_map_resolution")
            if 0 < len(context.selected_objects):
                layout.column().operator("shirakumo_trial.rebake", text="ReBake Selected")
            else:
                layout.column().operator("shirakumo_trial.rebake", text="ReBake All")
            layout.column().operator("shirakumo_trial.make_level", text="Make Level Geo")
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
    default_camera_offset: bpy.props.FloatVectorProperty(
        name="Default Camera Trigger Offset",
        default=[5,0,1.4137166], subtype='EULER', options=set(),
        description="The default offset of camera triggers")

registered_classes = [
    SHIRAKUMO_TRIAL_OT_rebake,
    SHIRAKUMO_TRIAL_OT_reexport,
    SHIRAKUMO_TRIAL_OT_make_level,
    SHIRAKUMO_TRIAL_OT_export_as_object,
    SHIRAKUMO_TRIAL_PT_edit_panel,
    SHIRAKUMO_TRIAL_file_properties,
]

def register():
    for cls in registered_classes:
        bpy.utils.register_class(cls)
    def clear_progress(_arg=None):
        for obj in bpy.context.scene.objects:
            if hasattr(obj, 'shirakumo_operator_progress'):
                obj.shirakumo_operator_progress = -1.0
    bpy.types.Object.shirakumo_operator_progress = bpy.props.FloatProperty(name="Progress", default=-1.0)
    bpy.types.Scene.shirakumo_trial_file_properties = bpy.props.PointerProperty(
        type=SHIRAKUMO_TRIAL_file_properties)
    bpy.app.handlers.load_post.append(clear_progress)

def unregister():
    del bpy.types.Object.shirakumo_operator_progress
    del bpy.types.Scene.shirakumo_trial_file_properties
    for cls in registered_classes:
        bpy.utils.unregister_class(cls)
