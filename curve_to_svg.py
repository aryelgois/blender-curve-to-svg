bl_info = {
    'name': "Export 2D Curve to SVG",
    'author': "Aryel Mota Góis",
    'version': (0, 0, 1),
    'blender': (2, 77, 0),
    'location': "Properties > Data > Export SVG",
    'description': "Generate a SVG file from selected 2D Curves",
    'warning': "Curve splines may be inverted, so self intersections can be wrong after export",
    'wiki_url': "https://github.com/aryelgois/blender-curve-to-svg",
    'tracker_url': "https://github.com/aryelgois/blender-curve-to-svg/issues",
    'category': "Import-Export"}


import bpy
from xml.etree import ElementTree
from xml.dom import minidom
from mathutils import Vector
from math import pi


VERSION = '.'.join(str(v) for v in (bl_info['version']))


def svg_transform(obj, precision):
    """Returns SVG transform for object"""

    loc = obj.location.to_2d().to_tuple(precision)
    scl = obj.scale.to_2d().to_tuple(precision)
    rot = round(obj.rotation_euler.z * 180 / pi, precision)
    result = []

    if rot:
        result.append("rotate({} {} {})".format(rot, *loc))

    if loc[0] or loc[1]:
        result.append("translate({} {})".format(*loc))

    if scl[0] != 1.0 or scl[1] != 1.0:
        result.append("scale({} {})".format(*scl))

    return ' '.join(result)


def to_hex(ch):
    """Converts linear channel to sRGB and then to hexadecimal"""
    # Author: @brecht
    # Link: https://devtalk.blender.org/t/get-hex-gamma-corrected-color/2422/2

    if ch < 0.0031308:
        srgb = 0.0 if ch < 0.0 else ch * 12.92
    else:
        srgb = ch ** (1.0 / 2.4) * 1.055 - 0.055

    return format(max(min(int(srgb * 255 + 0.5), 255), 0), '02x')

def col_to_hex(col):
    """Converts a Color object to hexadecimal"""

    return '#' + ''.join(to_hex(ch) for ch in col)


def pretty_xml(elem):
    """Returns a pretty-printed XML string for the Element"""

    rough_string = ElementTree.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent='  ')


class CurveExportSVGPanel(bpy.types.Panel):
    """Creates a Panel in the data context of the properties editor"""

    bl_label = "Export SVG"
    bl_idname = 'DATA_PT_exportsvg'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'data'

    def draw(self, context):
        """Draws the Export SVG Panel"""

        scene = context.scene
        layout = self.layout
        selected_2d_curve = False
        selected_other = False

        for obj in context.selected_objects:
            if obj.type == 'CURVE' and obj.data.dimensions == '2D':
                selected_2d_curve = True
            else:
                selected_other = True

        if selected_2d_curve:
            row = layout.row()
            row.prop(scene, 'export_svg_minify')

            row = layout.row()
            row.prop(scene, 'export_svg_scale')

            row = layout.row()
            row.prop(scene, 'export_svg_precision')

            row = layout.row()
            row.prop(scene, 'export_svg_output', text="")

            row = layout.row()
            row.operator('curve.export_svg', text="Export")

            if selected_other:
                layout.label(icon='ERROR', text="Notice: only selected 2D Curves will be exported")
        else:
            layout.label(icon='ERROR', text="You must select a 2D Curve")

            layout.label(text="Go to Shape panel and select 2D")

    @classmethod
    def poll(cls, context):
        """Checks if the Export SVG Panel should appear"""

        return context.object.type == 'CURVE'


class DATA_OT_CurveExportSVG(bpy.types.Operator):
    """Generates a SVG file from selected 2D Curves"""

    bl_label = "Export SVG"
    bl_idname = 'curve.export_svg'

    # guide https://css-tricks.com/svg-path-syntax-illustrated-guide/
    # will be used: M L C S Z
    commands = {
        'moveto':     "M {x},{y}",
        'lineto':     "L {x},{y}",
       #'lineto_h':   "H {x}",
       #'lineto_v':   "V {y}",
        'curveto':    "C {h1x},{h1y} {h2x},{h2y} {x},{y}",       # h = handle_point
        'curveto_s':  "S {h2x},{h2y} {x},{y}",                   # mirror handle from previous C or S
       #'curveto_q':  "Q {hx},{hy} {x},{y}",                     # both handles in same position
       #'curveto_qs': "T {x},{y}",                               # mirror handle from previous Q or T
       #'arc':        "A {rx},{ry} {rot} {arc} {sweep} {x},{y}", # arc, sweep -> 0 or 1. it's to choose between four possibilities of arc
        'closepath':  "Z"}

    #handle_type = {'AUTO', 'ALIGNED', 'VECTOR', 'FREE'}

    def execute(self, context):
        """Exports selected 2D Curves to SVG file"""

        scene = context.scene
        precision = scene.export_svg_precision
        scale = scene.export_svg_scale

        svg = ElementTree.Element('svg')
        svg.set('xmlns', "http://www.w3.org/2000/svg")
        svg.set('version', "1.1")
        svg.append(ElementTree.Comment(" Generated by blender-curve-to-svg v{} ".format(VERSION)))

        container = ElementTree.SubElement(svg, 'g')
        container.set('transform', "scale({0} -{0})".format(scale)) # the Y axis is inverted
        box = [0, 0, 0, 0]

        for obj in context.selected_objects:
            if obj.type != 'CURVE' or obj.data.dimensions != '2D':
                continue

            container.append(self.curve_to_svg(obj, precision))
            self.update_viewbox(box, obj, precision)

        box = [round(x * scale, precision) for x in box]
        svg.set('viewBox', ' '.join(str(x) for x in (box[0], -box[3], box[2] - box[0], box[3] - box[1])))

        if scene.export_svg_minify:
            result = "<?xml version=\"1.0\" ?>" + ElementTree.tostring(svg, 'unicode')
        else:
            result = pretty_xml(svg)

        f = open(scene.export_svg_output, 'w') # TODO: search if is there a better approach
        f.write(result)
        f.close()

        return {'FINISHED'}


    def curve_to_svg(self, obj, precision):
        """Converts a Curve object to SVG elements"""

        materials = obj.data.materials
        paths = {}

        for spline in obj.data.splines:
            id = spline.material_index
            d = self.spline_to_path(spline, precision)

            if id in paths:
                paths[id].extend(d)
            else:
                paths[id] = d

        if materials:
            container = ElementTree.Element('g')
            container.set('id', obj.name)

            transform = svg_transform(obj, precision)
            if transform:
                container.set('transform', transform)

            for id, d in paths.items():
                path = ElementTree.SubElement(container, 'path')
                material = materials[id]
                if material:
                    path.set('id', material.name)
                    path.set('style', "fill: {}".format(col_to_hex(material.diffuse_color)))
                path.set('d', ' '.join(d))

            return container

        path = ElementTree.Element('path')
        path.set('id', obj.name)

        transform = svg_transform(obj, precision)
        if transform:
            path.set('transform', transform)

        path.set('d', ' '.join(paths[0]))

        return path


    def spline_to_path(self, spline, precision):
        """Converts a Curve Spline to 'd' attribute for path element"""

        d = []
        prev = None

        # TODO: fix when points are in inverted order
        # problem: some paths do union instead of difference
        for point in spline.bezier_points:
            prev = self.add_command(d, point, prev, precision)

        if spline.use_cyclic_u:
            self.add_command(d, spline.bezier_points[0], prev, precision)
            d.append(self.commands['closepath'])

        return d


    def add_command(self, d, point, prev, precision):
        """Adds the path's next command, returns previous handler point"""

        p = point.co.to_2d().to_tuple(precision)
        values = {'x': p[0], 'y': p[1]}
        # TODO: type will be used to choose between L C S commands
        # C can do all the job, but using the others can reduce the svg
        l = (point.handle_left.to_2d().to_tuple(precision), point.handle_left_type)
        r = (point.handle_right.to_2d().to_tuple(precision), point.handle_right_type)

        # first command is moveto first point, then curveto others points
        if not d:
            command = self.commands['moveto'].format(**values)
        else:
            values.update({'h1x': prev[0][0], 'h1y': prev[0][1], 'h2x': l[0][0], 'h2y': l[0][1]})
            command = self.commands['curveto'].format(**values)

        d.append(command)

        return r


    def update_viewbox(self, vbox, obj, precision):
        """Updates viewBox coords to fit an object"""

        bbox = [(obj.matrix_world * Vector(corner)).to_tuple(precision) for corner in obj.bound_box]

        vbox[0] = min([vbox[0], bbox[0][0], bbox[1][0], bbox[2][0], bbox[3][0]])
        vbox[1] = min([vbox[1], bbox[0][1], bbox[1][1], bbox[4][1], bbox[5][1]])
        vbox[2] = max([vbox[2], bbox[4][0], bbox[5][0], bbox[6][0], bbox[7][0]])
        vbox[3] = max([vbox[3], bbox[2][1], bbox[3][1], bbox[6][1], bbox[7][1]])


def register():
    """Registers curve_to_svg Add-on"""

    bpy.types.Scene.export_svg_scale = bpy.props.IntProperty(
            name="Scale",
            description="How many pixels one blender unit represents",
            default=10,
            min=1)

    bpy.types.Scene.export_svg_precision = bpy.props.IntProperty(
            name="Precision",
            description="Precision of floating point Vectors",
            default=4,
            min=0,
            max=21)

    bpy.types.Scene.export_svg_minify = bpy.props.BoolProperty(
            name="Minify",
            description="SVG in one line",
            default=False)

    bpy.types.Scene.export_svg_output = bpy.props.StringProperty(
            name="Output",
            description="Path to output file",
            default="output.svg",
            subtype='FILE_PATH')

    bpy.utils.register_class(DATA_OT_CurveExportSVG)
    bpy.utils.register_class(CurveExportSVGPanel)


def unregister():
    """Unregisters curve_to_svg Add-on"""

    bpy.utils.unregister_class(CurveExportSVGPanel)
    bpy.utils.unregister_class(DATA_OT_CurveExportSVG)

    del bpy.types.Scene.export_svg_scale
    del bpy.types.Scene.export_svg_precision
    del bpy.types.Scene.export_svg_minify
    del bpy.types.Scene.export_svg_output


if __name__ == '__main__':
    register()
