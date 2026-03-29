from .utils import BaseCommonGeometryObject


class SphereWithMultipleHoles(BaseCommonGeometryObject):
    def __init__(self, sphere_radius=10, cylinder_radius=2):

        if cylinder_radius >= sphere_radius:
            raise ValueError("cylinder_radius should be less than sphere_radius")

        self.sphere_radius = sphere_radius
        self.cylinder_radius = cylinder_radius

    def csg_model(self, materials):
        import openmc

        r = self.sphere_radius
        cr = self.cylinder_radius

        sphere = openmc.Sphere(r=r, boundary_type="vacuum")
        x_cyl = openmc.XCylinder(r=cr)
        y_cyl = openmc.YCylinder(r=cr)
        z_cyl = openmc.ZCylinder(r=cr)

        region_material = -sphere & +x_cyl & +y_cyl & +z_cyl
        region_holes = -sphere & (-x_cyl | -y_cyl | -z_cyl)

        cell1 = openmc.Cell(region=region_material, fill=materials[0])
        cell2 = openmc.Cell(region=region_holes)

        geometry = openmc.Geometry([cell1, cell2])
        my_materials = openmc.Materials(materials)
        model = openmc.Model(geometry=geometry, materials=my_materials)
        return model

    def cadquery_assembly(self):
        import cadquery as cq

        r = self.sphere_radius
        cr = self.cylinder_radius
        cyl_len = r * 3

        sphere = cq.Workplane().sphere(r)
        z_hole = cq.Workplane("XY").cylinder(cyl_len, cr)
        x_hole = cq.Workplane("YZ").cylinder(cyl_len, cr)
        y_hole = cq.Workplane("XZ").cylinder(cyl_len, cr)

        result = sphere.cut(z_hole).cut(x_hole).cut(y_hole)

        assembly = cq.Assembly(name="sphere_with_multiple_holes")
        assembly.add(result)
        return assembly
