import math

from .utils import BaseCommonGeometryObject


class Paraboloid(BaseCommonGeometryObject):
    def __init__(self, focal_length=5, height=10):
        self.focal_length = focal_length
        self.height = height

    def csg_model(self, materials):
        import openmc

        f = self.focal_length
        h = self.height
        rim_radius = math.sqrt(2 * f * h)

        # Paraboloid surface: x² + y² - 2fz = 0
        # -quadric is where x² + y² - 2fz < 0, i.e. z > (x²+y²)/(2f) (above the surface)
        quadric = openmc.Quadric(a=1, b=1, j=-2 * f)

        z_top = openmc.ZPlane(z0=h, boundary_type="vacuum")
        z_bot = openmc.ZPlane(z0=-0.01, boundary_type="vacuum")
        outer_cyl = openmc.ZCylinder(r=rim_radius, boundary_type="vacuum")

        # Material region: inside the paraboloid surface and below the cap
        region_material = -quadric & -z_top & +z_bot
        # Void region: outside the paraboloid but inside the bounding box
        region_void = +quadric & -z_top & +z_bot & -outer_cyl

        cell1 = openmc.Cell(region=region_material, fill=materials[0])
        cell2 = openmc.Cell(region=region_void)

        geometry = openmc.Geometry([cell1, cell2])
        my_materials = openmc.Materials(materials)
        model = openmc.Model(geometry=geometry, materials=my_materials)
        return model

    def cadquery_assembly(self):
        import cadquery as cq

        f = self.focal_length
        h = self.height
        rim_radius = math.sqrt(2 * f * h)

        n = 100
        points = []
        for i in range(n + 1):
            r = rim_radius * i / n
            z = r**2 / (2 * f)
            points.append((r, z))

        profile = (
            cq.Workplane("XZ")
            .spline(points)
            .lineTo(0, h)
            .close()
            .revolve(360, (0, 0, 0), (0, 0, 1))
        )

        assembly = cq.Assembly(name="paraboloid")
        assembly.add(profile)
        return assembly
