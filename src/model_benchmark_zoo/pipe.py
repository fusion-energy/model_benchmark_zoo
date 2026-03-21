from .utils import BaseCommonGeometryObject

class Pipe(BaseCommonGeometryObject):
    def __init__(self, height=20, outer_radius=5, inner_radius=4):

        if inner_radius >= outer_radius:
            raise ValueError('inner_radius should be less than outer_radius')

        self.height = height
        self.outer_radius = outer_radius
        self.inner_radius = inner_radius

    def csg_model(self, materials):
        import openmc

        outer_cyl = openmc.ZCylinder(r=self.outer_radius, boundary_type="vacuum")
        inner_cyl = openmc.ZCylinder(r=self.inner_radius)
        z_top = openmc.ZPlane(z0=0.5 * self.height, boundary_type="vacuum")
        z_bot = openmc.ZPlane(z0=-0.5 * self.height, boundary_type="vacuum")

        region_wall = -outer_cyl & +inner_cyl & +z_bot & -z_top
        region_hole = -inner_cyl & +z_bot & -z_top

        cell1 = openmc.Cell(region=region_wall, fill=materials[0])
        cell2 = openmc.Cell(region=region_hole)

        geometry = openmc.Geometry([cell1, cell2])
        my_materials = openmc.Materials(materials)
        model = openmc.Model(geometry=geometry, materials=my_materials)
        return model

    def cadquery_assembly(self):
        import cadquery as cq

        assembly = cq.Assembly(name="pipe")
        outer = cq.Workplane("XY").cylinder(self.height, self.outer_radius)
        inner = cq.Workplane("XY").cylinder(self.height + 1, self.inner_radius)
        pipe = outer.cut(inner)
        assembly.add(pipe)
        return assembly
