from .utils import BaseCommonGeometryObject


class SteppedCylinder(BaseCommonGeometryObject):
    def __init__(self, height=20, large_radius=6, small_radius=3):

        if small_radius >= large_radius:
            raise ValueError("small_radius should be less than large_radius")

        self.height = height
        self.large_radius = large_radius
        self.small_radius = small_radius

    def csg_model(self, materials):
        import openmc

        h = self.height
        large_cyl = openmc.ZCylinder(r=self.large_radius, boundary_type="vacuum")
        small_cyl = openmc.ZCylinder(r=self.small_radius)
        z_bot = openmc.ZPlane(z0=-h / 2, boundary_type="vacuum")
        z_mid = openmc.ZPlane(z0=0)
        z_top = openmc.ZPlane(z0=h / 2, boundary_type="vacuum")

        # Lower section: full large cylinder
        region_lower = -large_cyl & +z_bot & -z_mid
        # Upper section: small cylinder only
        region_upper = -small_cyl & +z_mid & -z_top
        region_material = region_lower | region_upper

        # Void: upper half, between small and large cylinder
        region_void = +small_cyl & -large_cyl & +z_mid & -z_top

        cell1 = openmc.Cell(region=region_material, fill=materials[0])
        cell2 = openmc.Cell(region=region_void)

        geometry = openmc.Geometry([cell1, cell2])
        my_materials = openmc.Materials(materials)
        model = openmc.Model(geometry=geometry, materials=my_materials)
        return model

    def cadquery_assembly(self):
        import cadquery as cq

        h = self.height
        rl = self.large_radius
        rs = self.small_radius

        lower = cq.Solid.makeCylinder(
            rl, h / 2, pnt=cq.Vector(0, 0, -h / 2), dir=cq.Vector(0, 0, 1)
        )
        upper = cq.Solid.makeCylinder(
            rs, h / 2, pnt=cq.Vector(0, 0, 0), dir=cq.Vector(0, 0, 1)
        )
        result = cq.Workplane().add(lower).add(upper).combine()

        assembly = cq.Assembly(name="stepped_cylinder")
        assembly.add(result)
        return assembly
