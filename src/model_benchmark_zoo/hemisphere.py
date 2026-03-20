from .utils import BaseCommonGeometryObject

class Hemisphere(BaseCommonGeometryObject):
    def __init__(self, radius=10):
        self.radius = radius

    def csg_model(self, materials):
        import openmc

        sphere_surface = openmc.Sphere(r=self.radius, boundary_type="vacuum")
        z_plane = openmc.ZPlane(z0=0, boundary_type="vacuum")

        region = -sphere_surface & +z_plane
        cell = openmc.Cell(region=region, fill=materials[0])

        geometry = openmc.Geometry([cell])
        my_materials = openmc.Materials(materials)
        model = openmc.Model(geometry=geometry, materials=my_materials)
        return model

    def cadquery_assembly(self):
        import cadquery as cq

        assembly = cq.Assembly(name="hemisphere")
        sphere = cq.Workplane().sphere(self.radius)
        cut_box = cq.Workplane("XY").transformed(
            offset=(0, 0, -self.radius)
        ).box(self.radius * 3, self.radius * 3, self.radius * 2)
        hemisphere = sphere.cut(cut_box)
        assembly.add(hemisphere)
        return assembly
