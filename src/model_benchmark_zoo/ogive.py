import math

from .utils import BaseCommonGeometryObject

class Ogive(BaseCommonGeometryObject):
    def __init__(self, base_radius=5, length=15):
        self.base_radius = base_radius
        self.length = length

    def analytic_volumes(self):
        """Exact volume of the spherical cap the ogive is a section of."""
        return (
            math.pi * self.length
            * (3 * self.base_radius ** 2 + self.length ** 2) / 6,
        )

    def _csg_model(self, materials):
        import openmc

        R = self.base_radius
        L = self.length

        rho = (R**2 + L**2) / (2 * L)
        z_c = L - rho

        ogive_sphere = openmc.Sphere(z0=z_c, r=rho)
        z_base = openmc.ZPlane(z0=0, boundary_type="vacuum")
        z_tip = openmc.ZPlane(z0=L, boundary_type="vacuum")

        region_material = -ogive_sphere & +z_base & -z_tip

        cell1 = openmc.Cell(region=region_material, fill=materials[0])

        geometry = openmc.Geometry([cell1])
        my_materials = openmc.Materials(materials)
        model = openmc.Model(geometry=geometry, materials=my_materials)
        return model

    def cadquery_assembly(self):
        import cadquery as cq
        from OCP.BRepPrimAPI import BRepPrimAPI_MakeSphere, BRepPrimAPI_MakeBox
        from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut
        from OCP.gp import gp_Pnt

        R = self.base_radius
        L = self.length

        rho = (R**2 + L**2) / (2 * L)
        z_c = L - rho

        sphere = BRepPrimAPI_MakeSphere(gp_Pnt(0, 0, z_c), rho).Shape()
        big = 2 * rho + 2
        cut_box = BRepPrimAPI_MakeBox(
            gp_Pnt(-big, -big, -big), gp_Pnt(big, big, 0)
        ).Shape()
        ogive_shape = BRepAlgoAPI_Cut(sphere, cut_box).Shape()

        assembly = cq.Assembly(name="ogive")
        assembly.add(cq.Workplane().add(cq.Solid(ogive_shape)))
        return assembly
