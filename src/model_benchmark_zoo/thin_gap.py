from .utils import BaseCommonGeometryObject


class ThinGap(BaseCommonGeometryObject):
    def __init__(self, box_width=10, box_height=10, box_depth=10, gap=0.5):
        self.box_width = box_width
        self.box_height = box_height
        self.box_depth = box_depth
        self.gap = gap

    def csg_model(self, materials):
        import openmc

        w = self.box_width
        h = self.box_height
        d = self.box_depth
        g = self.gap

        x_min = openmc.XPlane(x0=-(w + g/2), boundary_type="vacuum")
        x_left = openmc.XPlane(x0=-g/2)
        x_right = openmc.XPlane(x0=g/2)
        x_max = openmc.XPlane(x0=(w + g/2), boundary_type="vacuum")
        y_min = openmc.YPlane(y0=-h/2, boundary_type="vacuum")
        y_max = openmc.YPlane(y0=h/2, boundary_type="vacuum")
        z_min = openmc.ZPlane(z0=-d/2, boundary_type="vacuum")
        z_max = openmc.ZPlane(z0=d/2, boundary_type="vacuum")

        yz_region = +y_min & -y_max & +z_min & -z_max

        region_left = +x_min & -x_left & yz_region
        region_gap = +x_left & -x_right & yz_region
        region_right = +x_right & -x_max & yz_region

        cell1 = openmc.Cell(region=region_left, fill=materials[0])
        cell2 = openmc.Cell(region=region_gap)  # void gap
        cell3 = openmc.Cell(region=region_right, fill=materials[1])

        geometry = openmc.Geometry([cell1, cell2, cell3])
        my_materials = openmc.Materials(materials)
        model = openmc.Model(geometry=geometry, materials=my_materials)
        return model

    def cadquery_assembly(self):
        import cadquery as cq

        w = self.box_width
        h = self.box_height
        d = self.box_depth
        g = self.gap

        assembly = cq.Assembly(name="thin_gap")

        # Left box: centered at x = -(w/2 + g/2)
        left = cq.Workplane("XY").transformed(offset=(-(w/2 + g/2), 0, 0)).box(w, h, d)
        assembly.add(left)

        # Right box: centered at x = (w/2 + g/2)
        right = cq.Workplane("XY").transformed(offset=((w/2 + g/2), 0, 0)).box(w, h, d)
        assembly.add(right)

        return assembly
