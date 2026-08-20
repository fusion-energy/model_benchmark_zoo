import math

from .utils import BaseCommonGeometryObject

class CylindricalIntersection(BaseCommonGeometryObject):
    def __init__(self, radius=3, length=20):
        self.radius = radius
        self.length = length

    def analytic_volumes(self):
        """Exact volume of the union, two cylinders less the Steinmetz solid they share."""
        return (
            2 * math.pi * self.radius ** 2 * self.length
            - 16 * self.radius ** 3 / 3,
        )

    def _csg_model(self, materials):
        import openmc

        r = self.radius
        l = self.length

        z_cyl = openmc.ZCylinder(r=r)
        x_cyl = openmc.XCylinder(r=r)

        # Bounding box
        x_min = openmc.XPlane(x0=-l/2, boundary_type="vacuum")
        x_max = openmc.XPlane(x0=l/2, boundary_type="vacuum")
        y_min = openmc.YPlane(y0=-l/2, boundary_type="vacuum")
        y_max = openmc.YPlane(y0=l/2, boundary_type="vacuum")
        z_min = openmc.ZPlane(z0=-l/2, boundary_type="vacuum")
        z_max = openmc.ZPlane(z0=l/2, boundary_type="vacuum")

        bounding = +x_min & -x_max & +y_min & -y_max & +z_min & -z_max

        # Material region: union of both cylinders inside bounding box
        region_mat = bounding & (-z_cyl | -x_cyl)

        # Void: inside bounding, outside both cylinders

        cell1 = openmc.Cell(region=region_mat, fill=materials[0])

        geometry = openmc.Geometry([cell1])
        my_materials = openmc.Materials(materials)
        model = openmc.Model(geometry=geometry, materials=my_materials)
        return model

    def cadquery_assembly(self):
        import cadquery as cq

        r = self.radius
        l = self.length

        assembly = cq.Assembly(name="cylindrical_intersection")

        z_cyl = cq.Workplane("XY").cylinder(l, r)
        x_cyl = cq.Workplane("YZ").cylinder(l, r)
        fused = z_cyl.union(x_cyl)

        assembly.add(fused)

        return assembly
