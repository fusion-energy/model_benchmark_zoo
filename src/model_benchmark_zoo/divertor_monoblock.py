from .utils import BaseCommonGeometryObject

class DivertorMonoblock(BaseCommonGeometryObject):
    def __init__(self, width=20, height=25, depth=12, pipe_outer_radius=6, pipe_inner_radius=5):
        self.width = width
        self.height = height
        self.depth = depth
        self.pipe_outer_radius = pipe_outer_radius
        self.pipe_inner_radius = pipe_inner_radius

    def csg_model(self, materials):
        import openmc

        w = self.width
        h = self.height
        d = self.depth
        ro = self.pipe_outer_radius
        ri = self.pipe_inner_radius

        box = openmc.model.RectangularParallelepiped(
            -w / 2, w / 2, -d / 2, d / 2, -h / 2, h / 2,
            boundary_type="vacuum"
        )
        outer_pipe = openmc.YCylinder(r=ro)
        inner_pipe = openmc.YCylinder(r=ri)

        region_block = -box & +outer_pipe
        region_pipe = -outer_pipe & +inner_pipe & -box
        region_void = -inner_pipe & -box

        cell1 = openmc.Cell(region=region_block, fill=materials[0])
        cell2 = openmc.Cell(region=region_pipe, fill=materials[1])
        cell3 = openmc.Cell(region=region_void)

        geometry = openmc.Geometry([cell1, cell2, cell3])
        my_materials = openmc.Materials(materials)
        model = openmc.Model(geometry=geometry, materials=my_materials)
        return model

    def cadquery_assembly(self):
        import cadquery as cq

        assembly = cq.Assembly(name="divertor_monoblock")

        w = self.width
        h = self.height
        d = self.depth
        ro = self.pipe_outer_radius
        ri = self.pipe_inner_radius

        # Pipe wall (annular, along Y axis)
        outer_pipe = cq.Workplane("XZ").cylinder(d, ro)
        inner_pipe = cq.Workplane("XZ").cylinder(d, ri)
        pipe_wall = outer_pipe.cut(inner_pipe)
        assembly.add(pipe_wall)

        # Block minus outer pipe
        block = cq.Workplane("XY").box(w, d, h)
        block_with_hole = block.cut(cq.Workplane("XZ").cylinder(d, ro))
        assembly.add(block_with_hole)

        return assembly
