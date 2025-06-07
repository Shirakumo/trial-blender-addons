import bpy
from bpy.types import Operator
from bpy_extras.io_utils import ExportHelper

def export_model(file, obj, config):
    vertices = []
    faces = []
    textures = []
    vertex_type = 1
    material_type = 0
    mesh = obj.data.meshes[0]
    mat = obj.data.materials[0]

    ## TODO: Split vertices where needed (UVs, normals, etc)
    
    if 0 < len(mesh.uv_layers):
        vertex_type = vertex_type | 2
    if 0 < len(mesh.color_attributes):
        vertex_type = vertex_type | 4
    if config['export_normals']:
        vertex_type = vertex_type | 8
    if config['export_tangents']:
        vertex_type = vertex_type | 16

    ## TODO: flatten vertex arrays together
    ## TODO: write out images
    
    # Kaitai serialization is really.... really.... annoyingly cumbersome
    model = Sf3Model()
    model.magic = b"\x81\x53\x46\x33\x00\xE0\xD0\x0D\x0A\x0A"
    model.format_id = b"\x05"
    model.checksum = 0
    model.null_terminator = b"\x00"
    mod = model.model = Sf3Model.Model(_parent=model)
    mod.format = Sf3Model.VertexFormat(_parent=mod)
    mod.format.raw = vertex_type
    mod.material_type = Sf3Model.MaterialType(_parent=mod)
    mod.material_type.raw = material_type
    mod.material_size = sum([str.len+2 for str in textures])
    mod.material = Sf3Model.Material(_parent=mod)
    mod.material.textures = textures
    mod.vertex_data = Sf3Model.VertexData(_parent=mod)
    mod.vertex_data.face_count = len(faces)
    mod.vertex_data.faces = faces
    mod.vertex_data.vertex_count = len(vertices)
    mod.vertex_data.vertices = vertices
    model._check()
    with open(file, 'wb') as stream:
        with KaitaiStream(stream) as _io:
            model._write(_io)
    return {'FINISHED'}

class ExportSF3(Operator, ExportHelper):
    bl_idname = 'export_scene.sf3'
    bl_label = 'Export SF3'
    
    filename_ext = 'sf3'
    filter_glob: bpy.props.StringProperty(default='*.sf3', options={'HIDDEN'})

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

    def invoke(self, context, event):
        return ExportHelper.invoke_popup(self, context, event)

    def execute(self, context):
        return self.export_sf3(context)

    def export_sf3(self, context):
        export_settings = {}
        return export_model(self.filepath, export_settings)

def menu_func_export(self, context):
    self.layout.operator(ExportSF3.bl_idname, text='Simple File Format Family (.sf3)')

def register():
    bpy.utils.register_class(ExportSF3)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)

def unregister():
    bpy.utils.unregister_class(ExportSF3)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
