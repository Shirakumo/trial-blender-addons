import bpy
from bpy.types import Operator
from bpy_extras.io_utils import ExportHelper

def export_model(file, config):
    pass

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
