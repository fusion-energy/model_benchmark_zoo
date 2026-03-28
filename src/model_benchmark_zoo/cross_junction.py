from .utils import BaseCommonGeometryObject


class CrossJunction(BaseCommonGeometryObject):
    def __init__(self, arm_length=10, arm_width=4, depth=4):
        self.arm_length = arm_length
        self.arm_width = arm_width
        self.depth = depth

    def csg_model(self, materials):
        import openmc

        al = self.arm_length
        aw = self.arm_width / 2
        d = self.depth / 2

        # Outer bounding planes (vacuum)
        x_min = openmc.XPlane(x0=-al, boundary_type="vacuum")
        x_max = openmc.XPlane(x0=al, boundary_type="vacuum")
        y_min = openmc.YPlane(y0=-al, boundary_type="vacuum")
        y_max = openmc.YPlane(y0=al, boundary_type="vacuum")
        z_bot = openmc.ZPlane(z0=-d, boundary_type="vacuum")
        z_top = openmc.ZPlane(z0=d, boundary_type="vacuum")

        # Inner bar-edge planes
        y_bar_min = openmc.YPlane(y0=-aw)
        y_bar_max = openmc.YPlane(y0=aw)
        x_bar_min = openmc.XPlane(x0=-aw)
        x_bar_max = openmc.XPlane(x0=aw)

        # Horizontal bar (including center overlap): mat1
        region_h = +x_min & -x_max & +y_bar_min & -y_bar_max & +z_bot & -z_top

        # Vertical bar top arm (above horizontal bar): mat2
        region_v_top = +x_bar_min & -x_bar_max & +y_bar_max & -y_max & +z_bot & -z_top
        # Vertical bar bottom arm (below horizontal bar): mat2
        region_v_bot = +x_bar_min & -x_bar_max & +y_min & -y_bar_min & +z_bot & -z_top

        # Four corner void regions
        region_void_1 = +x_bar_max & -x_max & +y_bar_max & -y_max & +z_bot & -z_top
        region_void_2 = +x_min & -x_bar_min & +y_bar_max & -y_max & +z_bot & -z_top
        region_void_3 = +x_min & -x_bar_min & +y_min & -y_bar_min & +z_bot & -z_top
        region_void_4 = +x_bar_max & -x_max & +y_min & -y_bar_min & +z_bot & -z_top

        cell1 = openmc.Cell(region=region_h, fill=materials[0])
        cell2 = openmc.Cell(region=region_v_top | region_v_bot, fill=materials[1])
        cell3 = openmc.Cell(
            region=region_void_1 | region_void_2 | region_void_3 | region_void_4
        )

        geometry = openmc.Geometry([cell1, cell2, cell3])
        my_materials = openmc.Materials(materials)
        model = openmc.Model(geometry=geometry, materials=my_materials)
        return model

    def cadquery_assembly(self):
        import cadquery as cq

        al = self.arm_length
        aw = self.arm_width
        d = self.depth

        assembly = cq.Assembly(name="cross_junction")

        h_bar = cq.Workplane("XY").box(2 * al, aw, d)
        assembly.add(h_bar)

        v_bar_full = cq.Workplane("XY").box(aw, 2 * al, d)
        h_bar_for_cut = cq.Workplane("XY").box(2 * al, aw, d)
        v_bar = v_bar_full.cut(h_bar_for_cut)
        assembly.add(v_bar)

        return assembly
