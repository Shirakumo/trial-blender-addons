import bpy
import bmesh
from pathlib import Path
from math import sqrt
from .utils import *

base_material_name = 'BaseMaterial'

def is_base_material(mat):
    return mat and mat.name.startswith(base_material_name)

def is_level_file():
    for obj in bpy.data.objects:
        if is_environment(obj):
            return True
    return False

def is_bakable_object(obj):
    return (obj.type == 'MESH' and
            (not obj.rigid_body or
             not obj.khr_physics_extra_props or
             not is_trigger(obj)))

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

def ensure_base_material_exists():
    if bpy.data.materials.get(base_material_name) is None:
        mat = bpy.data.materials.new(name=base_material_name)
        mat.use_nodes = True
    return bpy.data.materials[base_material_name]

def ensure_base_material(obj, force=True):
    def set():
        mat = ensure_base_material_exists().copy()
        obj.data.materials[0] = mat
        bsdf = mat.node_tree.nodes.get('Principled BSDF')
        if bsdf and 0 < len(bsdf.inputs['Base Color'].links):
            input = bsdf.inputs['Base Color'].links[0].from_node
            input.select = True
            mat.node_tree.nodes.active = input
    if 0 == len(obj.data.materials):
        obj.data.materials.append(None)
        set()
    elif obj.data.materials[0] is None:
        set()
    elif force and not is_base_material(obj.data.materials[0]):
        set()
    if obj.data.uv_layers.get("UVMap") is None:
        obj.data.uv_layers.new(name='UVMap')
    if obj.data.uv_layers.get("AO") is None:
        obj.data.uv_layers.new(name='AO')
    return obj.data.materials[0]

def ensure_ao_material(obj, size=None, resize=True):
    mat = ensure_base_material(obj, force=False)
    glTF = mat.node_tree.nodes.get('Group')
    if glTF is None:
        bpy.context.preferences.addons['io_scene_gltf2'].preferences.settings_node_ui = True
        original_type = bpy.context.area.type
        bpy.context.area.type = 'NODE_EDITOR'
        bpy.context.area.spaces.active.node_tree = mat.node_tree
        bpy.ops.node.gltf_settings_node_operator('INVOKE_DEFAULT')
        bpy.context.area.type = original_type
        glTF = mat.node_tree.nodes.get('Group')
    if 0 == len(glTF.inputs['Occlusion'].links):
        size = ao_size(obj, size)
        tex = mat.node_tree.nodes.new("ShaderNodeTexImage")
        tex.image = bpy.data.images.new("AO", size, size)
        mat.node_tree.links.new(glTF.inputs['Occlusion'], tex.outputs['Color'])

    tex = glTF.inputs['Occlusion'].links[0].from_node
    if resize:
        size = ao_size(obj, size)
        if tex.image.size[0] != size:
            tex.image.scale(size, size)
    return (mat, size, tex)

def is_solo_rebake(obj):
    return is_prop(obj) or (obj.rigid_body and not obj.khr_physics_extra_props.infinite_mass)

def rebake_object(obj, resize=True):
    print("Rebake "+obj.name)
    
    if is_solo_rebake(obj):
        hide_all(lambda obj : True)
        obj.hide_render = False
    else:
        hide_all(lambda obj : obj.rigid_body and not obj.khr_physics_extra_props.infinite_mass)

    with Selection([obj]) as sel:
        mat, size, tex = ensure_ao_material(obj, None, resize)
        bsdf = mat.node_tree.nodes.get('Principled BSDF')
        # Modify the material to make it opaque, otherwise the AO bake fucks up
        alpha = bsdf.inputs['Alpha']
        saved_normal = None
        if 0 < len(bsdf.inputs['Normal'].links):
            link = bsdf.inputs['Normal'].links[0]
            saved_normal = link.from_node
            mat.node_tree.links.remove(link)
        saved_alpha = alpha.default_value
        saved_uv = obj.data.uv_layers.active_index
        saved_node = mat.node_tree.nodes.active
        alpha.default_value = 1.0
        obj.data.uv_layers.active = obj.data.uv_layers["AO"]
        tex.select = True
        mat.node_tree.nodes.active = tex

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.smart_project(island_margin=1/size)
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.scene.render.engine = 'CYCLES'
        bpy.ops.object.bake('INVOKE_DEFAULT', type='AO', uv_layer='AO', use_clear=True)
        ## NOTE: This currently does not do much since Blender's bake runs in the
        ##       background, and changes shit after this returns, and we have no
        ##       way to observe when the job is done to restore our settings. Fun.
        ##       we try anyway by hoping 3 seconds is enough lol.
        def restore():
            alpha.default_value = saved_alpha
            obj.data.uv_layers.active_index = saved_uv
            for node in mat.node_tree.nodes:
                node.select = False
            saved_node.select = True
            mat.node_tree.nodes.active = saved_node
            if saved_normal:
                mat.node_tree.links.new(bsdf.inputs['Normal'], saved_normal.outputs['Color'])
        bpy.app.timers.register(restore, first_interval=3)

def export_single_object(obj=None, path=None):
    if obj is None:
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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Re-bake the ambient occlusion map and set it up if necessary."

    @classmethod
    def poll(cls, context):
        return context.object.shirakumo_operator_progress < 0
    
    def prepare(self, context, event):
        objects = context.selected_objects
        if len(objects) == 0:
            objects = bpy.data.objects
        for obj in unique_meshes(objects):
            if is_bakable_object(obj):
                self.steps.append(lambda o=obj : rebake_object(o))

class SHIRAKUMO_TRIAL_OT_reexport(SteppedOperator):
    bl_idname = "shirakumo_trial.reexport"
    bl_label = "ReExport"

    @classmethod
    def description(cls, context, properties):
        path = context.scene.shirakumo_trial_file_properties.export_path
        if path == '':
            return "Export the current file."
        else:
            return "Re-export the current file to "+path
    
    def prepare(self, context, event):
        path = bpy.path.abspath(context.scene.shirakumo_trial_file_properties.export_path)
        args = {"check_existing": False,
                "use_visible": True,
                "export_lights": True,
                "export_cameras": True,
                "export_def_bones": True,
                "export_texcoords": True,
                "export_normals": True,
                "export_materials": "EXPORT",
                "export_yup": True,
                "export_apply": is_level_file()}
        if path == '' or event.ctrl:
            self.steps.append(lambda : bpy.ops.export_scene.gltf('INVOKE_DEFAULT', **args))
        else:
            self.steps.append(lambda : bpy.ops.export_scene.gltf(filepath=path, **args))

class SHIRAKUMO_TRIAL_OT_make_environment(bpy.types.Operator):
    bl_idname = "shirakumo_trial.make_environment"
    bl_label = "Mark as Level Geo"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Turn the object into environment geometry by setting the corresponding physics properties and normalising its transform and geometry."
    
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
        for obj in objects:
            ensure_physics_object(obj, type='ENVIRONMENT')
            ensure_base_material(obj)
            ensure_ao_material(obj)
            obj.rigid_body.collision_shape = 'MESH'
            obj.khr_physics_extra_props.infinite_mass = True
        return {'FINISHED'}

class SHIRAKUMO_TRIAL_OT_make_prop(bpy.types.Operator):
    bl_idname = "shirakumo_trial.make_prop"
    bl_label = "Mark as Prop"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Turn the object a prop by setting its material and so on."
    
    def invoke(self, context, event):
        objects = context.selected_objects
        if len(objects) == 0:
            objects = bpy.data.objects
        objects = [ x for x in objects if x.type == 'MESH' ]
        push_selection(objects)
        for obj in objects:
            ensure_physics_object(obj, type='PROP')
            ensure_base_material(obj)
            ensure_ao_material(obj)
        return {'FINISHED'}

class SHIRAKUMO_TRIAL_OT_toggle_immovable(bpy.types.Operator):
    bl_idname = "shirakumo_trial.toggle_immovable"
    bl_label = "Toggle Immovable"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Turn the object into a fixed physics object that can't be moved or vice-versa."
    
    def invoke(self, context, event):
        objects = [ x for x in context.selected_objects if x.type == 'MESH' ]
        for obj in objects:
            obj.khr_physics_extra_props.infinite_mass = not obj.khr_physics_extra_props.infinite_mass
        return {'FINISHED'}

class SHIRAKUMO_TRIAL_OT_export_as_object(SteppedOperator):
    bl_idname = "shirakumo_trial.export_as_object"
    bl_label = "Export as Object"
    bl_description = "Export the selected object as a single glTF file."

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
    bl_category = "Item"
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout
        obj = context.object
        if not hasattr(obj, 'shirakumo_operator_progress'):
            pass
        elif 0 <= obj.shirakumo_operator_progress:
            layout.column().progress(text="Working..." , factor=obj.shirakumo_operator_progress)
        else:
            layout.column().prop(context.scene.shirakumo_trial_file_properties, "ao_map_resolution")
            if 0 < len(context.selected_objects):
                layout.column().operator("shirakumo_trial.rebake", text="ReBake AO for Selected")
                if not is_environment(obj) and not is_prop(obj):
                    layout.column().operator("shirakumo_trial.make_environment", text="Make Environment")
                    layout.column().operator("shirakumo_trial.make_prop", text="Make Prop")
                if is_prop(obj):
                    if obj.khr_physics_extra_props.infinite_mass:
                        layout.column().operator("shirakumo_trial.toggle_immovable", text="Make Movable")
                    else:
                        layout.column().operator("shirakumo_trial.toggle_immovable", text="Make Immovable")
                    layout.column().operator("shirakumo_trial.export_as_object", text="Export as Object")
            else:
                layout.column().operator("shirakumo_trial.rebake", text="ReBake AO for All")
            layout.column().operator("shirakumo_trial.reexport", text="ReExport GLB")

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
    SHIRAKUMO_TRIAL_OT_make_environment,
    SHIRAKUMO_TRIAL_OT_make_prop,
    SHIRAKUMO_TRIAL_OT_toggle_immovable,
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
