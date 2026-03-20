from .utils import BaseCommonGeometryObject

class SphereWithCylindricalHole(BaseCommonGeometryObject):
    def __init__(self, sphere_radius=10, cylinder_radius=2):

        if cylinder_radius >= sphere_radius:
            raise ValueError('cylinder_radius should be less than sphere_radius')

        self.sphere_radius = sphere_radius
        self.cylinder_radius = cylinder_radius

    def csg_model(self, materials):
        import openmc

        sphere_surface = openmc.Sphere(r=self.sphere_radius, boundary_type="vacuum")
        cylinder_surface = openmc.ZCylinder(r=self.cylinder_radius)

        region_material = -sphere_surface & +cylinder_surface
        region_hole = -sphere_surface & -cylinder_surface

        cell1 = openmc.Cell(region=region_material, fill=materials[0])
        cell2 = openmc.Cell(region=region_hole)

        geometry = openmc.Geometry([cell1, cell2])
        my_materials = openmc.Materials(materials)
        model = openmc.Model(geometry=geometry, materials=my_materials)
        return model

    def cadquery_assembly(self):
        import cadquery as cq

        assembly = cq.Assembly(name="sphere_with_cylindrical_hole")
        sphere = cq.Workplane().sphere(self.sphere_radius)
        cylinder = cq.Workplane("XY").cylinder(self.sphere_radius * 3, self.cylinder_radius)
        result = sphere.cut(cylinder)
        assembly.add(result)
        return assembly
