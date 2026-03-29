import math

from .utils import BaseCommonGeometryObject

class AnnularSector(BaseCommonGeometryObject):
    def __init__(self, inner_radius=3, outer_radius=6, height=10, angle=90):
        self.inner_radius = inner_radius
        self.outer_radius = outer_radius
        self.height = height
        self.angle = angle

    def csg_model(self, materials):
        import openmc

        ri = self.inner_radius
        ro = self.outer_radius
        h = self.height

        inner_cyl = openmc.ZCylinder(r=ri)
        outer_cyl = openmc.ZCylinder(r=ro, boundary_type="vacuum")
        z_top = openmc.ZPlane(z0=h / 2, boundary_type="vacuum")
        z_bot = openmc.ZPlane(z0=-h / 2, boundary_type="vacuum")
        x_plane = openmc.XPlane(x0=0, boundary_type="vacuum")
        y_plane = openmc.YPlane(y0=0, boundary_type="vacuum")

        region_material = +inner_cyl & -outer_cyl & +z_bot & -z_top & +x_plane & +y_plane
        region_void = -inner_cyl & +z_bot & -z_top & +x_plane & +y_plane

        cell1 = openmc.Cell(region=region_material, fill=materials[0])
        cell2 = openmc.Cell(region=region_void)

        geometry = openmc.Geometry([cell1, cell2])
        my_materials = openmc.Materials(materials)
        model = openmc.Model(geometry=geometry, materials=my_materials)
        return model

    def cadquery_assembly(self):
        import cadquery as cq

        ri = self.inner_radius
        ro = self.outer_radius
        h = self.height
        angle = self.angle

        # Create rectangular cross-section in XZ plane and revolve
        profile = (
            cq.Workplane("XZ")
            .moveTo(ri, -h / 2)
            .lineTo(ro, -h / 2)
            .lineTo(ro, h / 2)
            .lineTo(ri, h / 2)
            .close()
        )
        sector = profile.revolve(angle, (0, 0, 0), (0, 0, 1))

        assembly = cq.Assembly(name="annular_sector")
        assembly.add(sector)
        return assembly
