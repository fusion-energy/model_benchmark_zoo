from .utils import BaseCommonGeometryObject


class ThinWalledCylinder(BaseCommonGeometryObject):
    def __init__(self, height=20, outer_radius=5, wall_thickness=0.2):

        if wall_thickness >= outer_radius:
            raise ValueError("wall_thickness should be less than outer_radius")

        self.height = height
        self.outer_radius = outer_radius
        self.wall_thickness = wall_thickness

    def csg_model(self, materials):
        import openmc

        r_out = self.outer_radius
        r_in = r_out - self.wall_thickness

        outer_cyl = openmc.ZCylinder(r=r_out, boundary_type="vacuum")
        inner_cyl = openmc.ZCylinder(r=r_in)
        z_top = openmc.ZPlane(z0=self.height / 2, boundary_type="vacuum")
        z_bot = openmc.ZPlane(z0=-self.height / 2, boundary_type="vacuum")

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

        r_out = self.outer_radius
        r_in = r_out - self.wall_thickness
        h = self.height

        assembly = cq.Assembly(name="thin_walled_cylinder")
        outer = cq.Workplane("XY").cylinder(h, r_out)
        inner = cq.Workplane("XY").cylinder(h + 1, r_in)
        pipe = outer.cut(inner)
        assembly.add(pipe)
        return assembly
