import math

from .utils import BaseCommonGeometryObject


class ToroidalSector(BaseCommonGeometryObject):
    def __init__(self, major_radius=10, minor_radius=2, angle=90):
        self.major_radius = major_radius
        self.minor_radius = minor_radius
        self.angle = angle

    def csg_model(self, materials):
        import openmc

        R = self.major_radius
        r = self.minor_radius
        theta = math.radians(self.angle)

        torus = openmc.ZTorus(a=R, b=r, c=r)

        # Sector from angle 0 to theta, centered on positive x-axis
        # Lower cutting plane: y = 0, keep +y side
        y_plane = openmc.YPlane(y0=0)

        # Upper cutting plane at angle theta from x-axis
        # Plane: sin(theta)*x - cos(theta)*y = 0
        upper_plane = openmc.Plane(
            a=math.sin(theta), b=-math.cos(theta), c=0, d=0
        )

        # Bounding cylinder
        outer_cyl = openmc.ZCylinder(r=R + r + 1, boundary_type="vacuum")
        z_top = openmc.ZPlane(z0=r + 1, boundary_type="vacuum")
        z_bot = openmc.ZPlane(z0=-(r + 1), boundary_type="vacuum")

        region_material = -torus & +y_plane & +upper_plane
        region_void = (
            -outer_cyl & +z_bot & -z_top
            & (+torus | -y_plane | -upper_plane)
        )

        cell1 = openmc.Cell(region=region_material, fill=materials[0])
        cell2 = openmc.Cell(region=region_void)

        geometry = openmc.Geometry([cell1, cell2])
        my_materials = openmc.Materials(materials)
        model = openmc.Model(geometry=geometry, materials=my_materials)
        return model

    def cadquery_assembly(self):
        import cadquery as cq

        R = self.major_radius
        r = self.minor_radius

        assembly = cq.Assembly(name="toroidal_sector")
        solid = (
            cq.Workplane("XZ")
            .center(R, 0)
            .circle(r)
            .revolve(self.angle, (0, 0, 0), (0, 0, 1))
        )
        assembly.add(solid)
        return assembly
