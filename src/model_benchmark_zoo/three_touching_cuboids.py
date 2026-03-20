from .utils import BaseCommonGeometryObject

#     *------*------*
#     | mat1 | mat2 |
#     *------*------*
#     | mat3 | void |
#     *------*------*
#
# 2x2 grid of cuboids sharing faces, 3 filled with materials, 1 void (source)

class ThreeTouchingCuboids(BaseCommonGeometryObject):
    def __init__(self, width=5):
        self.width = width

    def csg_model(self, materials):
        import openmc

        w = self.width

        x_left = openmc.XPlane(x0=-w, boundary_type="vacuum")
        x_mid = openmc.XPlane(x0=0)
        x_right = openmc.XPlane(x0=w, boundary_type="vacuum")
        y_bot = openmc.YPlane(y0=-w, boundary_type="vacuum")
        y_mid = openmc.YPlane(y0=0)
        y_top = openmc.YPlane(y0=w, boundary_type="vacuum")
        z_bot = openmc.ZPlane(z0=-0.5 * w, boundary_type="vacuum")
        z_top = openmc.ZPlane(z0=0.5 * w, boundary_type="vacuum")

        # mat1: top-left
        region1 = +x_left & -x_mid & +y_mid & -y_top & +z_bot & -z_top
        # mat2: top-right
        region2 = +x_mid & -x_right & +y_mid & -y_top & +z_bot & -z_top
        # mat3: bottom-left
        region3 = +x_left & -x_mid & +y_bot & -y_mid & +z_bot & -z_top
        # void: bottom-right (source location)
        region4 = +x_mid & -x_right & +y_bot & -y_mid & +z_bot & -z_top

        cell1 = openmc.Cell(region=region1, fill=materials[0])
        cell2 = openmc.Cell(region=region2, fill=materials[1])
        cell3 = openmc.Cell(region=region3, fill=materials[2])
        cell4 = openmc.Cell(region=region4)

        geometry = openmc.Geometry([cell1, cell2, cell3, cell4])
        my_materials = openmc.Materials(materials)
        model = openmc.Model(geometry=geometry, materials=my_materials)
        return model

    def cadquery_assembly(self):
        import cadquery as cq

        w = self.width
        assembly = cq.Assembly(name="three_touching_cuboids")

        # mat1: top-left, center at (-w/2, w/2, 0)
        cuboid1 = cq.Workplane().transformed(
            offset=(-0.5 * w, 0.5 * w, 0)
        ).box(w, w, w)
        assembly.add(cuboid1)

        # mat2: top-right, center at (w/2, w/2, 0)
        cuboid2 = cq.Workplane().transformed(
            offset=(0.5 * w, 0.5 * w, 0)
        ).box(w, w, w)
        assembly.add(cuboid2)

        # mat3: bottom-left, center at (-w/2, -w/2, 0)
        cuboid3 = cq.Workplane().transformed(
            offset=(-0.5 * w, -0.5 * w, 0)
        ).box(w, w, w)
        assembly.add(cuboid3)

        return assembly
