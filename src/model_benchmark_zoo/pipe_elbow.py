from .utils import BaseCommonGeometryObject


class PipeElbow(BaseCommonGeometryObject):
    def __init__(self, bend_radius=10, outer_radius=3, inner_radius=2):

        if inner_radius >= outer_radius:
            raise ValueError("inner_radius should be less than outer_radius")

        self.bend_radius = bend_radius
        self.outer_radius = outer_radius
        self.inner_radius = inner_radius

    def csg_model(self, materials):
        import openmc

        R = self.bend_radius
        r_out = self.outer_radius
        r_in = self.inner_radius

        outer_torus = openmc.ZTorus(a=R, b=r_out, c=r_out)
        inner_torus = openmc.ZTorus(a=R, b=r_in, c=r_in)

        # 90-degree sector in first quadrant
        x_plane = openmc.XPlane(x0=0)
        y_plane = openmc.YPlane(y0=0)

        # Bounding
        outer_cyl = openmc.ZCylinder(r=R + r_out + 1, boundary_type="vacuum")
        z_top = openmc.ZPlane(z0=r_out + 1, boundary_type="vacuum")
        z_bot = openmc.ZPlane(z0=-(r_out + 1), boundary_type="vacuum")

        region_wall = -outer_torus & +inner_torus & +x_plane & +y_plane
        region_void = (
            -outer_cyl & +z_bot & -z_top
            & (+outer_torus | -inner_torus | -x_plane | -y_plane)
        )

        cell1 = openmc.Cell(region=region_wall, fill=materials[0])
        cell2 = openmc.Cell(region=region_void)

        geometry = openmc.Geometry([cell1, cell2])
        my_materials = openmc.Materials(materials)
        model = openmc.Model(geometry=geometry, materials=my_materials)
        return model

    def cadquery_assembly(self):
        import cadquery as cq

        R = self.bend_radius
        r_out = self.outer_radius
        r_in = self.inner_radius

        outer = (
            cq.Workplane("XZ")
            .center(R, 0)
            .circle(r_out)
            .revolve(90, (0, 0, 0), (0, 0, 1))
        )
        inner = (
            cq.Workplane("XZ")
            .center(R, 0)
            .circle(r_in)
            .revolve(90, (0, 0, 0), (0, 0, 1))
        )
        result = outer.cut(inner)

        assembly = cq.Assembly(name="pipe_elbow")
        assembly.add(result)
        return assembly
