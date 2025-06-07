import bpy
import os
from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper
from .sf3.sf3_model import Sf3Model

def import_model(file, config):
    mod = Sf3Model.from_file(file)
    pass

class ImportSF3(Operator, ImportHelper):
    bl_idname = 'import_scene.sf3'
    bl_label = 'Import SF3'
    bl_options = {'REGISTER', 'UNDO'}
    
    filter_glob: bpy.props.StringProperty(default="*.sf3", options={'HIDDEN'})
    
    files: bpy.props.CollectionProperty(
        name="File Path",
        type=bpy.types.OperatorFileListElement,
    )

    def draw(self, context):
        layout = self.layout

        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

    def invoke(self, context, event):
        return ImportHelper.invoke_popup(self, context)

    def execute(self, context):
        return self.import_sf3(context)

    def import_sf3(self, context):
        import_settings = {}
        if self.files:
            ret = {'CANCELLED'}
            dirname = os.path.dirname(self.filepath)
            for file in self.files:
                path = os.path.join(dirname, file.name)
                if import_model(path, import_settings) == {'FINISHED'}:
                    ret = {'FINISHED'}
            return ret
        else:
            return import_model(self.filepath, import_settings)

def menu_func_import(self, context):
    self.layout.operator(ImportSF3.bl_idname, text='Simple File Format Family (.sf3)')

def register():
    bpy.utils.register_class(ImportSF3)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)

def unregister():
    bpy.utils.unregister_class(ImportSF3)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)

