import math

from .utils import BaseCommonGeometryObject

class Cone(BaseCommonGeometryObject):
    def __init__(self, height=10, base_radius=5):
        self.height = height
        self.base_radius = base_radius

    def csg_model(self, materials):
        import openmc

        h = self.height
        r = self.base_radius

        # Apex at top, base at bottom
        cone = openmc.ZCone(z0=h / 2, r2=(r / h) ** 2)
        z_top = openmc.ZPlane(z0=h / 2, boundary_type="vacuum")
        z_bot = openmc.ZPlane(z0=-h / 2, boundary_type="vacuum")
        outer_cyl = openmc.ZCylinder(r=r, boundary_type="vacuum")

        region_material = -cone & +z_bot & -z_top
        region_void = +cone & -outer_cyl & +z_bot & -z_top

        cell1 = openmc.Cell(region=region_material, fill=materials[0])
        cell2 = openmc.Cell(region=region_void)

        geometry = openmc.Geometry([cell1, cell2])
        my_materials = openmc.Materials(materials)
        model = openmc.Model(geometry=geometry, materials=my_materials)
        return model

    def cadquery_assembly(self):
        import cadquery as cq

        h = self.height
        r = self.base_radius

        # Use OCC cone primitive, centered so base is at -h/2 and apex at h/2
        solid = cq.Solid.makeCone(
            r, 0, h, pnt=cq.Vector(0, 0, -h / 2), dir=cq.Vector(0, 0, 1)
        )

        assembly = cq.Assembly(name="cone")
        assembly.add(solid)
        return assembly
