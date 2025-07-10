import bpy
import math
from bpy_extras import view3d_utils
from mathutils import Vector, Matrix

def snap_to_line(p, a, b, clamp=False):
    s = b - a
    w = p - a
    ps = w.dot(s)
    if ps <= 0 and clamp:
        return a
    l2 = s.dot(s)
    if ps >= l2 and clamp:
        closest = b
    else:
        closest = a + ps / l2 * s
    return closest

def snap_to_grid(p, grid=0.1, basis=Matrix.Identity(4)):
    p = basis.inverted_safe() @ p
    r = [*p]
    for i in range(len(r)):
        r[i] = round((r[i])/grid)*granularity
    return basis @ Vector(r)

def edge_segment(edge):
    pass

def edge_face(edge):
    pass

def edge_basis(edge, origin):
    pass

class SHIRAKUMO_RECT_OT_draw_rectangle(bpy.types.Operator):
    bl_idname = "shirakumo_rect.draw_rectangle"
    bl_label = "Draw rectangle"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Draw a rectangle"

    grid: bpy.props.FloatProperty(
        name="Grid",
        default=0.1, options=set(),
        description="The grid size used for snapping rectangles")
    basis: Matrix.Identity(4)
    start: Vector()
    
    def modal(self, context, event):
        context.area.tag_redraw()
        
        if event.type == 'MOUSEMOVE':
            mouse_pos = (event.mouse_region_x, event.mouse_region_y)

        elif event.type == 'LEFTMOUSE':
            mouse_pos = (event.mouse_region_x, event.mouse_region_y)
            return {'FINISHED'}

        elif event.type == 'RIGHTMOUSE':
            return {'FINISHED'}
        elif event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            return {'PASS_THROUGH'}
        return {'RUNNING_MODAL'}

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        mouse_pos = (event.mouse_region_x, event.mouse_region_y)
        region = context.region
        region3D = context.space_data.region_3d
        view_vector = view3d_utils.region_2d_to_vector_3d(region, region3D, mouse_pos)
        start = view3d_utils.region_2d_to_location_3d(region, region3D, mouse_pos, view_vector)
        
        edge = None
        if edge:
            segment = edge_segment(edge)
            start = snap_to_line(pos, segment[0], segment[1])
            start = snap_to_grid(start, self.grid, basis=self.basis)
            self.basis = edge_basis(edge, start)
        else:
            start = snap_to_grid(start, self.grid, basis=self.basis)
            self.basis = Matrix.Translation(start)
        self.start = start
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

class SHIRAKUMO_RECT_WT_rectangle(bpy.types.WorkSpaceTool):
    bl_space_type = 'VIEW_3D'
    bl_context_mode = 'EDIT_MESH'
    bl_idname = 'SHIRAKUMO_rectangle_tools.rectangle_tool'
    bl_label = 'Rectangle Tool'
    bl_description = (
        'Extend geometry via rectangles'
    )
    bl_icon = 'ops.gpencil.primitive_box'
    bl_widget = 'VIEW3D_GGT_mesh_preselect_elem'
    bl_keymap = (
        ("shirakumo_rect.draw_rectangle", {"type": 'LEFTMOUSE', "value": 'PRESS'},
         {"properties": []}),
    )

registered_classes = [
    SHIRAKUMO_RECT_OT_draw_rectangle,
]

def register():
    for cls in registered_classes:
        bpy.utils.register_class(cls)
    bpy.utils.register_tool(SHIRAKUMO_RECT_WT_rectangle, after={'builtin.poly_build'})

def unregister():
    bpy.utils.unregister_tool(SHIRAKUMO_RECT_WT_rectangle)
    for cls in registered_classes:
        bpy.utils.unregister_class(cls)
