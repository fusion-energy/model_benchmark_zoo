import math

from .utils import BaseCommonGeometryObject

class Hyperboloid(BaseCommonGeometryObject):
    def __init__(self, waist_radius=3, top_radius=5, height=10):

        if top_radius <= waist_radius:
            raise ValueError('top_radius should be greater than waist_radius')
        if waist_radius <= 0:
            raise ValueError('waist_radius should be greater than 0')

        self.waist_radius = waist_radius
        self.top_radius = top_radius
        self.height = height

    def analytic_volumes(self):
        """Exact volume of the hyperboloid of one sheet.

        The radius grows as r(z) squared = a squared (1 + z squared / c squared),
        with c the same scale the CSG quadric uses, so integrating pi r squared over
        the height gives pi a squared (h + h cubed / (12 c squared)).
        """
        c = (0.5 * self.height) / math.sqrt(
            (self.top_radius / self.waist_radius) ** 2 - 1
        )
        return (
            math.pi * self.waist_radius ** 2
            * (self.height + self.height ** 3 / 12 / c ** 2),
        )

    def _csg_model(self, materials):
        import openmc

        a = self.waist_radius
        c = (0.5 * self.height) / math.sqrt((self.top_radius / self.waist_radius) ** 2 - 1)

        # Hyperboloid of one sheet: x²/a² + y²/a² - z²/c² = 1
        # openmc.Quadric: Ax² + By² + Cz² + Dxy + Eyz + Fxz + Gx + Hy + Jz + K = 0
        # So: (1/a²)x² + (1/a²)y² + (-1/c²)z² + (-1) = 0
        quadric = openmc.Quadric(
            a=1.0 / a**2,
            b=1.0 / a**2,
            c=-1.0 / c**2,
            k=-1.0,
        )

        z_top = openmc.ZPlane(z0=0.5 * self.height, boundary_type="vacuum")
        z_bot = openmc.ZPlane(z0=-0.5 * self.height, boundary_type="vacuum")

        region_material = -quadric & +z_bot & -z_top

        cell1 = openmc.Cell(region=region_material, fill=materials[0])

        geometry = openmc.Geometry([cell1])
        my_materials = openmc.Materials(materials)
        model = openmc.Model(geometry=geometry, materials=my_materials)
        return model

    def cadquery_assembly(self):
        import cadquery as cq

        a = self.waist_radius
        c = (0.5 * self.height) / math.sqrt((self.top_radius / self.waist_radius) ** 2 - 1)

        # Build a half-hyperbola profile in XZ plane
        n = 100
        points = []
        for i in range(n + 1):
            z = -0.5 * self.height + self.height * i / n
            r = a * math.sqrt(1 + (z / c) ** 2)
            points.append((r, z))

        # Create profile: line to hyperbola start, spline along curve, line back to axis, close
        # Include points[0] in the spline so it starts exactly at the lineTo endpoint
        profile = (
            cq.Workplane("XZ")
            .moveTo(0, points[0][1])
            .lineTo(points[0][0], points[0][1])
            .spline(points)
            .lineTo(0, points[-1][1])
            .close()
        )

        solid = profile.revolve(360, (0, 0), (0, 1))

        assembly = cq.Assembly(name="hyperboloid")
        assembly.add(solid)
        return assembly
