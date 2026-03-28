from .utils import BaseCommonGeometryObject


class EccentricNestedCylinders(BaseCommonGeometryObject):
    def __init__(self, height=20, outer_radius=6, inner_radius=2, offset=2):

        if inner_radius + offset >= outer_radius:
            raise ValueError(
                "inner cylinder must fit inside outer cylinder: "
                "inner_radius + offset must be less than outer_radius"
            )

        self.height = height
        self.outer_radius = outer_radius
        self.inner_radius = inner_radius
        self.offset = offset

    def csg_model(self, materials):
        import openmc

        h = self.height
        outer_cyl = openmc.ZCylinder(r=self.outer_radius, boundary_type="vacuum")
        inner_cyl = openmc.ZCylinder(x0=self.offset, y0=0, r=self.inner_radius)
        z_top = openmc.ZPlane(z0=h / 2, boundary_type="vacuum")
        z_bot = openmc.ZPlane(z0=-h / 2, boundary_type="vacuum")

        region_inner = -inner_cyl & +z_bot & -z_top
        region_outer = -outer_cyl & +inner_cyl & +z_bot & -z_top

        cell1 = openmc.Cell(region=region_inner, fill=materials[0])
        cell2 = openmc.Cell(region=region_outer, fill=materials[1])

        geometry = openmc.Geometry([cell1, cell2])
        my_materials = openmc.Materials(materials)
        model = openmc.Model(geometry=geometry, materials=my_materials)
        return model

    def cadquery_assembly(self):
        import cadquery as cq

        h = self.height

        assembly = cq.Assembly(name="eccentric_nested_cylinders")

        inner = cq.Workplane("XY").transformed(
            offset=(self.offset, 0, 0)
        ).cylinder(h, self.inner_radius)
        assembly.add(inner)

        outer = cq.Workplane("XY").cylinder(h, self.outer_radius)
        inner_for_cut = cq.Workplane("XY").transformed(
            offset=(self.offset, 0, 0)
        ).cylinder(h, self.inner_radius)
        outer_shell = outer.cut(inner_for_cut)
        assembly.add(outer_shell)

        return assembly
