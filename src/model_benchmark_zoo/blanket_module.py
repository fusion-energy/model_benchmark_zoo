from .utils import BaseCommonGeometryObject

class BlanketModule(BaseCommonGeometryObject):
    def __init__(self, outer_width=30, outer_height=40, outer_depth=20, wall_thickness=3, channel_radius=2):
        self.outer_width = outer_width
        self.outer_height = outer_height
        self.outer_depth = outer_depth
        self.wall_thickness = wall_thickness
        self.channel_radius = channel_radius

    def csg_model(self, materials):
        import openmc

        ow = self.outer_width
        oh = self.outer_height
        od = self.outer_depth
        wt = self.wall_thickness
        cr = self.channel_radius

        iw = ow - 2 * wt
        ih = oh - 2 * wt
        id_ = od - 2 * wt

        outer_box = openmc.model.RectangularParallelepiped(
            -ow / 2, ow / 2, -od / 2, od / 2, -oh / 2, oh / 2,
            boundary_type="vacuum"
        )
        inner_box = openmc.model.RectangularParallelepiped(
            -iw / 2, iw / 2, -id_ / 2, id_ / 2, -ih / 2, ih / 2
        )
        channel = openmc.YCylinder(r=cr)

        region_wall = -outer_box & +inner_box
        region_breeder = -inner_box & +channel
        region_channel = -channel & -inner_box

        cell1 = openmc.Cell(region=region_wall, fill=materials[0])
        cell2 = openmc.Cell(region=region_breeder, fill=materials[1])
        cell3 = openmc.Cell(region=region_channel, fill=materials[2])

        geometry = openmc.Geometry([cell1, cell2, cell3])
        my_materials = openmc.Materials(materials)
        model = openmc.Model(geometry=geometry, materials=my_materials)
        return model

    def cadquery_assembly(self):
        import cadquery as cq

        assembly = cq.Assembly(name="blanket_module")

        ow = self.outer_width
        oh = self.outer_height
        od = self.outer_depth
        wt = self.wall_thickness
        cr = self.channel_radius

        iw = ow - 2 * wt
        ih = oh - 2 * wt
        id_ = od - 2 * wt

        # Channel cylinder (along Y axis)
        channel = cq.Workplane("XZ").cylinder(id_, cr)
        assembly.add(channel)

        # Breeder: inner box minus channel
        inner_box = cq.Workplane("XY").box(iw, id_, ih)
        breeder = inner_box.cut(cq.Workplane("XZ").cylinder(id_, cr))
        assembly.add(breeder)

        # Wall: outer box minus inner box
        outer_box = cq.Workplane("XY").box(ow, od, oh)
        wall = outer_box.cut(cq.Workplane("XY").box(iw, id_, ih))
        assembly.add(wall)

        return assembly
