from .utils import BaseCommonGeometryObject

class TruncatedCone(BaseCommonGeometryObject):
    def __init__(self, height=10, bottom_radius=5, top_radius=2):

        if bottom_radius <= top_radius:
            raise ValueError('bottom_radius should be greater than top_radius')
        if top_radius <= 0:
            raise ValueError('top_radius should be greater than 0')

        self.height = height
        self.bottom_radius = bottom_radius
        self.top_radius = top_radius

    def csg_model(self, materials):
        import openmc

        h = self.height
        r_bot = self.bottom_radius
        r_top = self.top_radius

        # Cone apex is above the frustum where the two radii converge to zero
        z_apex = 0.5 * h * (r_top + r_bot) / (r_bot - r_top)
        # Slope parameter r2 = (R/Z)^2
        r2 = ((r_bot - r_top) / h) ** 2

        cone_surface = openmc.ZCone(z0=z_apex, r2=r2)
        z_top = openmc.ZPlane(z0=0.5 * h, boundary_type="vacuum")
        z_bot = openmc.ZPlane(z0=-0.5 * h, boundary_type="vacuum")

        region = -cone_surface & +z_bot & -z_top
        cell = openmc.Cell(region=region, fill=materials[0])

        geometry = openmc.Geometry([cell])
        my_materials = openmc.Materials(materials)
        model = openmc.Model(geometry=geometry, materials=my_materials)
        return model

    def cadquery_assembly(self):
        import cadquery as cq

        assembly = cq.Assembly(name="truncated_cone")
        frustum = (
            cq.Workplane("XY")
            .transformed(offset=(0, 0, -0.5 * self.height))
            .circle(self.bottom_radius)
            .workplane(offset=self.height)
            .circle(self.top_radius)
            .loft()
        )
        assembly.add(frustum)
        return assembly
