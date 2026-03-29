from .utils import BaseCommonGeometryObject

class Ogive(BaseCommonGeometryObject):
    def __init__(self, base_radius=5, length=15):
        self.base_radius = base_radius
        self.length = length

    def csg_model(self, materials):
        import openmc

        R = self.base_radius
        L = self.length

        rho = (R**2 + L**2) / (2 * L)
        z_c = L - rho

        ogive_sphere = openmc.Sphere(z0=z_c, r=rho)
        z_base = openmc.ZPlane(z0=0, boundary_type="vacuum")
        z_tip = openmc.ZPlane(z0=L, boundary_type="vacuum")
        outer_cyl = openmc.ZCylinder(r=R + 1, boundary_type="vacuum")

        region_material = -ogive_sphere & +z_base & -z_tip
        region_void = +ogive_sphere & +z_base & -z_tip & -outer_cyl

        cell1 = openmc.Cell(region=region_material, fill=materials[0])
        cell2 = openmc.Cell(region=region_void)

        geometry = openmc.Geometry([cell1, cell2])
        my_materials = openmc.Materials(materials)
        model = openmc.Model(geometry=geometry, materials=my_materials)
        return model

    def cadquery_assembly(self):
        import cadquery as cq

        R = self.base_radius
        L = self.length

        rho = (R**2 + L**2) / (2 * L)
        z_c = L - rho

        # Create sphere at the generating center
        sphere = cq.Workplane("XY").transformed(offset=(0, 0, z_c)).sphere(rho)
        # Cut everything below z=0
        big = 2 * rho + 2
        cut_below = cq.Workplane("XY").transformed(offset=(0, 0, -big / 2)).box(2 * big, 2 * big, big)
        ogive = sphere.cut(cut_below)

        assembly = cq.Assembly(name="ogive")
        assembly.add(ogive)
        return assembly
