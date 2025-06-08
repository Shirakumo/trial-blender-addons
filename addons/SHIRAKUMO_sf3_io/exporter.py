import bpy
import os
from bpy.types import Operator
from bpy_extras.io_utils import ExportHelper

def save_image(file, src_image, config):
    if config.image_type == 'None':
        return file
    image = src_image.copy()
    image.update()
    image.scale(*src_image.size)
    if config.image_type != 'AUTO':
        image.file_format = config.image_type
    image.filepath_raw = file
    if file_format in ["JPEG", "WEBP"]:
        image.save(quality=config['image_quality'])
    else:
        image.save()
    bpy.data.images.remove(image, do_unlink=True)

def export_model(file, obj, config):
    print("Exporting to "+file)
    dir = os.path.dirname(file)
    vertices = []
    faces = []
    textures = []
    vertex_type = 1
    material_type = 0
    mesh = obj.data.meshes[0]
    
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

    if 0 < len(obj.data.materials):
        nodes = obj.data.materials[0].node_tree.nodes
        bsdf = nodes.get("Principled BSDF")
        outp = nodes.get("Material Output")
        def try_add(input, bit):
            if 0 < len(input.links):
                tex = save_image(os.path.join(dir, name), input.links[0].image, config)
                if tex:
                    material_type = material_type | bit
                    textures.append(tex)
        
        try_add(bsdf.inputs('Base Color'), 'albedo', 1)
        try_add(bsdf.inputs('Normal'), 'normal', 2)
        if 0 == material_type & 0b111100:
            try_add(bsdf.inputs('Specular Tint'), 'specular', 64)
        try_add(bsdf.inputs('Emission Color'), 'emissive', 128)
        # TODO: decode metallic and separated mro
    
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

    image_type: bpy.props.EnumProperty(
        name='Images',
        items=(('AUTO', 'Automatic', 'Save images in their original format, or PNG'),
               ('PNG', 'PNG Format', 'Save images as lossless PNGs'),
               ('BMP', 'BitMaP Format', 'Save images as lossless, uncompressed BMPs'),
               ('TGA', 'Targa Format', 'Save images as lossless, uncompressed TGAs'),
               ('JPEG', 'JPEG Format', 'Same images as lossy JPEGs'),
               ('WEBP', 'WebP Format', 'Save images as lossy WebPs'),
               ('NONE', 'None', 'Don\'t export images')),
        description='Output format for images.',
        default='AUTO',
    )
    image_quality: bpy.props.IntProperty(
        name='Image Quality',
        description='The quality of the image for compressed formats',
        default=80, min=1, max=100,
    )
    export_normals: bpy.props.BoolProperty(
        name='Export Normals',
        description='Whether to export normal vectors',
        default=True,
    )
    export_tangents: bpy.props.BoolProperty(
        name='Export Tangents',
        description='Whether to export tangent vectors',
        default=False,
    )

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        header, body = layout.panel('SF3_export_data', default_closed=False)
        header.label(text='Data')
        if body:
            body.prop(self, 'export_normals')
            body.prop(self, 'export_tangents')
        header, body = layout.panel('SF3_export_material', default_closed=False)
        header.label(text='Material')
        if body:
            body.prop(self, 'image_type')
            body.prop(self, 'image_quality')

    def invoke(self, context, event):
        return ExportHelper.invoke(self, context, event)

    def execute(self, context):
        return self.export_sf3(context)

    def export_sf3(self, context):
        config = {
            'filepath': self.filepath,
            'image_type': self.image_type,
            'image_quality': self.image_quality,
            'export_normals': self.export_normals,
            'export_tangents': self.export_tangents,
        }
        return export_model(self.filepath, config)

def menu_func_export(self, context):
    self.layout.operator(ExportSF3.bl_idname, text='Simple File Format Family (.sf3)')

def register():
    bpy.utils.register_class(ExportSF3)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)

def unregister():
    bpy.utils.unregister_class(ExportSF3)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
