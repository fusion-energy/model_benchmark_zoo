from .utils import BaseCommonGeometryObject
class Ellipticaltorus(BaseCommonGeometryObject):
    def __init__(self, major_radius=10, minor_radius1=2, minor_radius2=1):
        """
        input: minor_radius1 parallel to axis of revolution, minor_radius2 perpendicular to axis of revolution
        """
        self.major_radius = major_radius
        self.minor_radius1 = minor_radius1
        self.minor_radius2 = minor_radius2

    def csg_model(self, materials):
        import openmc

        surface = openmc.ZTorus(a=self.major_radius, b=self.minor_radius1, c=self.minor_radius2)
        # A torus is not convex, so a particle leaving the inner surface can cross
        # the hole and re-enter on the far side of the ring. Putting the vacuum
        # boundary on the torus surface itself would kill those particles, while
        # the CAD model transports them because dagmc_model wraps the geometry
        # with bounded_universe, which leaves a void region around it. Enclose the
        # torus in a void so both models describe the same transport problem.
        boundary = openmc.Sphere(
            r=2 * (self.major_radius + max(self.minor_radius1, self.minor_radius2)),
            boundary_type="vacuum"
        )
        region = -surface
        cell = openmc.Cell(region=region)
        cell.fill = materials[0]
        surrounding_void = openmc.Cell(region=+surface & -boundary)
        my_materials = openmc.Materials(materials)
        geometry = openmc.Geometry([cell, surrounding_void])
        model = openmc.Model(geometry=geometry, materials=my_materials)
        return model

    def cadquery_assembly(self):
        import cadquery as cq

        assembly = cq.Assembly(name="ellipticaltorus")
        ellipticaltorus1 = cq.Workplane("XZ", origin=(self.major_radius, 0, 0)).ellipse(self.minor_radius2, self.minor_radius1).revolve(180, (-self.major_radius,0,0), (-self.major_radius,1,0))
        ellipticaltorus2 = cq.Workplane("XZ", origin=(-self.major_radius, 0, 0)).ellipse(self.minor_radius2, self.minor_radius1).revolve(180, (self.major_radius,0,0), (self.major_radius,1,0))
        ellipticaltorus = ellipticaltorus1.union(ellipticaltorus2)        
        assembly.add(ellipticaltorus)
        return assembly
