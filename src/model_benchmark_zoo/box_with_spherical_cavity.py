from .utils import BaseCommonGeometryObject

class BoxWithSphericalCavity(BaseCommonGeometryObject):
    def __init__(self, width=10, sphere_radius=3):

        if sphere_radius >= width / 2:
            raise ValueError('sphere_radius should be less than half the width')

        self.width = width
        self.sphere_radius = sphere_radius

    def csg_model(self, materials):
        import openmc

        box_surface = openmc.model.RectangularParallelepiped(
            -0.5 * self.width,
            0.5 * self.width,
            -0.5 * self.width,
            0.5 * self.width,
            -0.5 * self.width,
            0.5 * self.width,
            boundary_type="vacuum"
        )
        sphere_surface = openmc.Sphere(r=self.sphere_radius)

        region_material = -box_surface & +sphere_surface
        region_cavity = -box_surface & -sphere_surface

        cell1 = openmc.Cell(region=region_material, fill=materials[0])
        cell2 = openmc.Cell(region=region_cavity)

        geometry = openmc.Geometry([cell1, cell2])
        my_materials = openmc.Materials(materials)
        model = openmc.Model(geometry=geometry, materials=my_materials)
        return model

    def cadquery_assembly(self):
        import cadquery as cq

        assembly = cq.Assembly(name="box_with_spherical_cavity")
        box = cq.Workplane().box(self.width, self.width, self.width)
        sphere = cq.Workplane().sphere(self.sphere_radius)
        result = box.cut(sphere)
        assembly.add(result)
        return assembly
