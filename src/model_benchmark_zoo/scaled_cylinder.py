import math

from .utils import BaseCommonGeometryObject

class ScaledCylinder(BaseCommonGeometryObject):
    """One shape emitted at any absolute size, to sweep scale on its own.

    Everything in the zoo sits within about a decade of 10 units except
    :class:`SimpleTokamak`, which is 1200 units across and needs its own hand
    picked edge lengths before it will mesh at all. That leaves no way to tell a
    genuine geometry failure from a model that has merely outgrown a setting, since
    the only two data points differ in shape as well as in size.

    ``scale`` multiplies the shape without changing its proportions, so a sweep
    over 1e-2, 1e0, 1e2 and 1e4 varies nothing else. Anything that then breaks is
    coupling to an absolute tolerance rather than a property of the geometry.

    A cylinder is used because its faces are governed by both kinds of setting at
    once: the curved face is refined by chord deflection, which is a length, and by
    angular tolerance, which is not, while the two flat caps have no curvature to
    be refined by at all. A sweep therefore shows which settings track the model
    and which stay put.
    """

    def __init__(self, radius=5, height=10, scale=1.0):
        if radius <= 0 or height <= 0:
            raise ValueError("radius and height must both be positive")
        if scale <= 0:
            raise ValueError("scale must be positive")
        self.radius = radius
        self.height = height
        self.scale = scale

    @property
    def scaled_radius(self):
        return self.radius * self.scale

    @property
    def scaled_height(self):
        return self.height * self.scale

    def analytic_volumes(self):
        """Exact volume at the current scale, pi r squared times the height."""
        return (
            math.pi * self.scaled_radius ** 2 * self.scaled_height,
        )

    def _csg_model(self, materials):
        import openmc

        cylinder = openmc.ZCylinder(r=self.scaled_radius, boundary_type="vacuum")
        z_top = openmc.ZPlane(z0=self.scaled_height / 2, boundary_type="vacuum")
        z_bot = openmc.ZPlane(z0=-self.scaled_height / 2, boundary_type="vacuum")

        region = -cylinder & +z_bot & -z_top

        cell = openmc.Cell(region=region, fill=materials[0])

        geometry = openmc.Geometry([cell])
        my_materials = openmc.Materials(materials)
        model = openmc.Model(geometry=geometry, materials=my_materials)
        return model

    def cadquery_assembly(self):
        import cadquery as cq

        assembly = cq.Assembly(name="scaled_cylinder")
        assembly.add(
            cq.Workplane("XY").cylinder(self.scaled_height, self.scaled_radius)
        )
        return assembly
