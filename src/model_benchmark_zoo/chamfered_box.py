from .utils import BaseCommonGeometryObject

class ChamferedBox(BaseCommonGeometryObject):
    def __init__(self, width=10, chamfer=1.5):
        if chamfer >= width / 2:
            raise ValueError('chamfer must be less than half the width')
        self.width = width
        self.chamfer = chamfer

    def csg_model(self, materials):
        import openmc

        w = self.width
        c = self.chamfer
        hw = w / 2

        # Six faces of the box
        x_right = openmc.XPlane(x0=hw, boundary_type="vacuum")
        x_left = openmc.XPlane(x0=-hw, boundary_type="vacuum")
        y_right = openmc.YPlane(y0=hw, boundary_type="vacuum")
        y_left = openmc.YPlane(y0=-hw, boundary_type="vacuum")
        z_top = openmc.ZPlane(z0=hw, boundary_type="vacuum")
        z_bot = openmc.ZPlane(z0=-hw, boundary_type="vacuum")

        # 12 chamfer planes, one per edge
        # d = hw + (hw - c) = w - c for 45-degree chamfers
        d = w - c

        # 4 edges parallel to Z (XY corners)
        chamfer_xy_pp = openmc.Plane(a=1, b=1, c=0, d=d, boundary_type="vacuum")   # +x +y
        chamfer_xy_pn = openmc.Plane(a=1, b=-1, c=0, d=d, boundary_type="vacuum")  # +x -y
        chamfer_xy_np = openmc.Plane(a=-1, b=1, c=0, d=d, boundary_type="vacuum")  # -x +y
        chamfer_xy_nn = openmc.Plane(a=-1, b=-1, c=0, d=d, boundary_type="vacuum") # -x -y

        # 4 edges parallel to Y (XZ corners)
        chamfer_xz_pp = openmc.Plane(a=1, b=0, c=1, d=d, boundary_type="vacuum")   # +x +z
        chamfer_xz_pn = openmc.Plane(a=1, b=0, c=-1, d=d, boundary_type="vacuum")  # +x -z
        chamfer_xz_np = openmc.Plane(a=-1, b=0, c=1, d=d, boundary_type="vacuum")  # -x +z
        chamfer_xz_nn = openmc.Plane(a=-1, b=0, c=-1, d=d, boundary_type="vacuum") # -x -z

        # 4 edges parallel to X (YZ corners)
        chamfer_yz_pp = openmc.Plane(a=0, b=1, c=1, d=d, boundary_type="vacuum")   # +y +z
        chamfer_yz_pn = openmc.Plane(a=0, b=1, c=-1, d=d, boundary_type="vacuum")  # +y -z
        chamfer_yz_np = openmc.Plane(a=0, b=-1, c=1, d=d, boundary_type="vacuum")  # -y +z
        chamfer_yz_nn = openmc.Plane(a=0, b=-1, c=-1, d=d, boundary_type="vacuum") # -y -z

        region = (
            +x_left & -x_right & +y_left & -y_right & +z_bot & -z_top
            & -chamfer_xy_pp & -chamfer_xy_pn & -chamfer_xy_np & -chamfer_xy_nn
            & -chamfer_xz_pp & -chamfer_xz_pn & -chamfer_xz_np & -chamfer_xz_nn
            & -chamfer_yz_pp & -chamfer_yz_pn & -chamfer_yz_np & -chamfer_yz_nn
        )

        cell = openmc.Cell(region=region, fill=materials[0])
        geometry = openmc.Geometry([cell])
        my_materials = openmc.Materials(materials)
        model = openmc.Model(geometry=geometry, materials=my_materials)
        return model

    def cadquery_assembly(self):
        import cadquery as cq

        assembly = cq.Assembly(name="chamfered_box")
        box = cq.Workplane("XY").box(self.width, self.width, self.width)
        chamfered = box.edges().chamfer(self.chamfer)
        assembly.add(chamfered)
        return assembly
