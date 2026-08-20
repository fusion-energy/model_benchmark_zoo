import math

from .utils import BaseCommonGeometryObject

class Ellipsoid(BaseCommonGeometryObject):
    def __init__(self, equatorial_radius=10, polar_radius=5):
        self.equatorial_radius = equatorial_radius
        self.polar_radius = polar_radius

    def analytic_volumes(self):
        """Exact volume of the spheroid, 4/3 pi a squared c."""
        return (
            4 / 3 * math.pi * self.equatorial_radius ** 2
            * self.polar_radius,
        )

    def _csg_model(self, materials):
        import openmc

        a = self.equatorial_radius
        c = self.polar_radius

        surface = openmc.Quadric(
            a=1 / a**2,
            b=1 / a**2,
            c=1 / c**2,
            k=-1,
        )
        bounding_sphere = openmc.Sphere(r=max(a, c) + 1, boundary_type="vacuum")

        region_material = -surface & -bounding_sphere

        cell1 = openmc.Cell(region=region_material, fill=materials[0])

        geometry = openmc.Geometry([cell1])
        my_materials = openmc.Materials(materials)
        model = openmc.Model(geometry=geometry, materials=my_materials)
        return model

    def cadquery_assembly(self):
        import cadquery as cq

        a = self.equatorial_radius
        c = self.polar_radius

        # Create half-ellipse profile in XZ plane and revolve around Z
        n = 100
        points = []
        for i in range(n + 1):
            angle = math.pi * i / n
            x = a * math.sin(angle)
            z = c * math.cos(angle)
            points.append((x, z))

        solid = (
            cq.Workplane("XZ")
            .spline(points)
            .close()
            .revolve(360, (0, 0), (0, 1))
        )

        assembly = cq.Assembly(name="ellipsoid")
        assembly.add(solid)
        return assembly
