from .utils import BaseCommonGeometryObject
class Circulartorus(BaseCommonGeometryObject):
    def __init__(self, major_radius=10, minor_radius=1):
        self.major_radius = major_radius
        self.minor_radius = minor_radius

    def csg_model(self, materials):
        import openmc

        surface = openmc.ZTorus(
            a=self.major_radius,
            b=self.minor_radius,
            c=self.minor_radius,
        )
        # A torus is not convex, so a particle leaving the inner surface can cross
        # the hole and re-enter on the far side of the ring. Putting the vacuum
        # boundary on the torus surface itself would kill those particles, while
        # the CAD model transports them because dagmc_model wraps the geometry
        # with bounded_universe, which leaves a void region around it. Enclose the
        # torus in a void so both models describe the same transport problem.
        boundary = openmc.Sphere(
            r=2 * (self.major_radius + self.minor_radius),
            boundary_type="vacuum"
        )
        region = -surface
        cell = openmc.Cell(region=region)
        cell.fill = materials[0]
        surrounding_void = openmc.Cell(region=+surface & -boundary)
        geometry = openmc.Geometry([cell, surrounding_void])
        my_materials = openmc.Materials(materials)
        model = openmc.Model(geometry=geometry, materials=my_materials)
        return model

    def cadquery_assembly(self):
        import cadquery as cq

        assembly = cq.Assembly(name="circulartorus")
        circulartorus = cq.Solid.makeTorus(self.major_radius, self.minor_radius)
        assembly.add(circulartorus)
        return assembly