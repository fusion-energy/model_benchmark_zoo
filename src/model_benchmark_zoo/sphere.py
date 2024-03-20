from .utils import BaseCommonGeometryObject

class Sphere(BaseCommonGeometryObject):
    def __init__(self, radius=10):
        self.radius = radius

    def csg_model(self, materials):
        import openmc

        surface = openmc.Sphere(r=self.radius, boundary_type="vacuum")
        region = -surface
        cell = openmc.Cell(region=region)
        cell.fill = materials[0]
        geometry = openmc.Geometry([cell])
        my_materials = openmc.Materials(materials)
        model = openmc.Model(geometry=geometry, materials=my_materials)
        return model

    def cadquery_assembly(self):
        import cadquery as cq

        assembly = cq.Assembly(name="sphere")
        sphere = cq.Workplane().sphere(self.radius)
        assembly.add(sphere)
        return assembly
