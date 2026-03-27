from .utils import BaseCommonGeometryObject

class LShaped(BaseCommonGeometryObject):
    def __init__(self, length=10, width=10, leg_thickness=3, height=5):
        self.length = length
        self.width = width
        self.leg_thickness = leg_thickness
        self.height = height

    def csg_model(self, materials):
        import openmc

        l = self.length
        w = self.width
        t = self.leg_thickness
        h = self.height

        # Center the L at origin
        ox = -w / 2
        oy = -l / 2

        z_bot = openmc.ZPlane(z0=-h / 2, boundary_type="vacuum")
        z_top = openmc.ZPlane(z0=h / 2, boundary_type="vacuum")

        # Horizontal leg: full width, thickness t at the bottom
        x_h_left = openmc.XPlane(x0=ox, boundary_type="vacuum")
        x_h_right = openmc.XPlane(x0=ox + w, boundary_type="vacuum")
        y_h_bot = openmc.YPlane(y0=oy, boundary_type="vacuum")
        y_h_top = openmc.YPlane(y0=oy + t)

        # Vertical leg: thickness t, full length
        x_v_right = openmc.XPlane(x0=ox + t)
        y_v_top = openmc.YPlane(y0=oy + l, boundary_type="vacuum")

        region_horiz = +x_h_left & -x_h_right & +y_h_bot & -y_h_top & +z_bot & -z_top
        region_vert = +x_h_left & -x_v_right & +y_h_top & -y_v_top & +z_bot & -z_top

        region = region_horiz | region_vert

        cell = openmc.Cell(region=region, fill=materials[0])

        # Void region: the notch area
        region_notch = +x_v_right & -x_h_right & +y_h_top & -y_v_top & +z_bot & -z_top
        cell_void = openmc.Cell(region=region_notch)

        geometry = openmc.Geometry([cell, cell_void])
        my_materials = openmc.Materials(materials)
        model = openmc.Model(geometry=geometry, materials=my_materials)
        return model

    def cadquery_assembly(self):
        import cadquery as cq

        l = self.length
        w = self.width
        t = self.leg_thickness
        h = self.height

        ox = -w / 2
        oy = -l / 2

        # L-shaped profile
        pts = [
            (ox, oy),
            (ox + w, oy),
            (ox + w, oy + t),
            (ox + t, oy + t),
            (ox + t, oy + l),
            (ox, oy + l),
        ]

        assembly = cq.Assembly(name="l_shaped")
        l_shape = (
            cq.Workplane("XY")
            .transformed(offset=(0, 0, -h / 2))
            .moveTo(*pts[0])
            .polyline(pts[1:])
            .close()
            .extrude(h)
        )
        assembly.add(l_shape)
        return assembly
