import math

from .utils import BaseCommonGeometryObject

class Capsule(BaseCommonGeometryObject):
    def __init__(self, radius=5, cylinder_height=10):
        self.radius = radius
        self.cylinder_height = cylinder_height

    def analytic_volumes(self):
        """Exact volume, the barrel plus one whole sphere of end caps."""
        return (
            math.pi * self.radius ** 2 * self.cylinder_height
            + 4 / 3 * math.pi * self.radius ** 3,
        )

    def _csg_model(self, materials):
        import openmc

        r = self.radius
        h = self.cylinder_height

        # Barrel cylinder
        barrel_cyl = openmc.ZCylinder(r=r)

        # Hemispheres at top and bottom
        top_sphere = openmc.Sphere(z0=h / 2, r=r)
        bot_sphere = openmc.Sphere(z0=-h / 2, r=r)

        # Planes separating barrel from caps
        z_mid_top = openmc.ZPlane(z0=h / 2)
        z_mid_bot = openmc.ZPlane(z0=-h / 2)

        # Capsule region: top cap | bottom cap | barrel
        region_material = (
            (-top_sphere & +z_mid_top) |
            (-bot_sphere & -z_mid_bot) |
            (-barrel_cyl & +z_mid_bot & -z_mid_top)
        )

        # Bounding surfaces



        cell1 = openmc.Cell(region=region_material, fill=materials[0])

        geometry = openmc.Geometry([cell1])
        my_materials = openmc.Materials(materials)
        model = openmc.Model(geometry=geometry, materials=my_materials)
        return model

    def cadquery_assembly(self):
        import cadquery as cq

        r = self.radius
        h = self.cylinder_height

        # Make the barrel cylinder
        barrel = cq.Workplane("XY").cylinder(h, r)
        # Make full spheres at top and bottom
        top_sphere = cq.Workplane("XY").transformed(offset=(0, 0, h / 2)).sphere(r)
        bot_sphere = cq.Workplane("XY").transformed(offset=(0, 0, -h / 2)).sphere(r)
        # Union all three to create the capsule shape
        capsule = barrel.union(top_sphere).union(bot_sphere)

        assembly = cq.Assembly(name="capsule")
        assembly.add(capsule)
        return assembly
