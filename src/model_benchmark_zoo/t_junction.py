from .utils import BaseCommonGeometryObject

class TJunction(BaseCommonGeometryObject):
    def __init__(self, main_length=20, main_width=5, branch_length=10, branch_width=5, height=5):
        self.main_length = main_length
        self.main_width = main_width
        self.branch_length = branch_length
        self.branch_width = branch_width
        self.height = height

    def csg_model(self, materials):
        import openmc

        ml = self.main_length
        mw = self.main_width
        bl = self.branch_length
        bw = self.branch_width
        h = self.height

        # Bounding box (vacuum on all outer faces)
        x_left = openmc.XPlane(x0=-ml / 2, boundary_type="vacuum")
        x_right = openmc.XPlane(x0=ml / 2, boundary_type="vacuum")
        y_bot = openmc.YPlane(y0=-mw / 2, boundary_type="vacuum")
        y_top = openmc.YPlane(y0=mw / 2 + bl, boundary_type="vacuum")
        z_bot = openmc.ZPlane(z0=-h / 2, boundary_type="vacuum")
        z_top = openmc.ZPlane(z0=h / 2, boundary_type="vacuum")

        # Internal dividing planes
        y_interface = openmc.YPlane(y0=mw / 2)
        x_branch_left = openmc.XPlane(x0=-bw / 2)
        x_branch_right = openmc.XPlane(x0=bw / 2)

        # Main bar: full width, below interface
        region_main = +x_left & -x_right & +y_bot & -y_interface & +z_bot & -z_top

        # Branch: narrow, above interface
        region_branch = +x_branch_left & -x_branch_right & +y_interface & -y_top & +z_bot & -z_top

        # Void: above interface, to the left of branch
        region_void_left = +x_left & -x_branch_left & +y_interface & -y_top & +z_bot & -z_top
        # Void: above interface, to the right of branch
        region_void_right = +x_branch_right & -x_right & +y_interface & -y_top & +z_bot & -z_top

        cell1 = openmc.Cell(region=region_main, fill=materials[0])
        cell2 = openmc.Cell(region=region_branch, fill=materials[1])
        cell3 = openmc.Cell(region=region_void_left)
        cell4 = openmc.Cell(region=region_void_right)

        geometry = openmc.Geometry([cell1, cell2, cell3, cell4])
        my_materials = openmc.Materials(materials)
        model = openmc.Model(geometry=geometry, materials=my_materials)
        return model

    def cadquery_assembly(self):
        import cadquery as cq

        ml = self.main_length
        mw = self.main_width
        bl = self.branch_length
        bw = self.branch_width
        h = self.height

        assembly = cq.Assembly(name="t_junction")

        # Main bar centered at origin
        main = cq.Workplane("XY").box(ml, mw, h)
        assembly.add(main)

        # Branch centered above main bar
        branch = cq.Workplane("XY").transformed(
            offset=(0, mw / 2 + bl / 2, 0)
        ).box(bw, bl, h)
        assembly.add(branch)

        return assembly
