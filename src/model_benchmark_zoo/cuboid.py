from .utils import BaseCommonGeometryObject

class Cuboid(BaseCommonGeometryObject):
    def __init__(self, width=10):
        self.width = width

    def csg_model(self, materials):
        import openmc
        
        surface = openmc.model.RectangularParallelepiped(
            -0.5*self.width,
            0.5*self.width,
            -0.5*self.width,
            0.5*self.width,
            -0.5*self.width,
            0.5*self.width,
            boundary_type="vacuum"
        )
        region = -surface
        cell = openmc.Cell(region=region)
        cell.fill = materials[0]
        geometry = openmc.Geometry([cell])
        my_materials = openmc.Materials(materials)
        model = openmc.Model(geometry=geometry, materials=my_materials)
        return model

    def cadquery_assembly(self):
        import cadquery as cq

        assembly = cq.Assembly(name="cuboid")
        Cuboid = cq.Workplane().box(self.width, self.width, self.width)
        assembly.add(Cuboid)
        return assembly
