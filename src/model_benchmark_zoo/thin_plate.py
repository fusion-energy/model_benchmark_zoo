from .utils import BaseCommonGeometryObject

class ThinPlate(BaseCommonGeometryObject):
    def __init__(self, length=10, width=10, thickness=0.5):
        self.length = length
        self.width = width
        self.thickness = thickness

    def csg_model(self, materials):
        import openmc

        surface = openmc.model.RectangularParallelepiped(
            -self.length / 2, self.length / 2,
            -self.width / 2, self.width / 2,
            -self.thickness / 2, self.thickness / 2,
            boundary_type="vacuum"
        )
        region = -surface
        cell = openmc.Cell(region=region, fill=materials[0])
        geometry = openmc.Geometry([cell])
        my_materials = openmc.Materials(materials)
        model = openmc.Model(geometry=geometry, materials=my_materials)
        return model

    def cadquery_assembly(self):
        import cadquery as cq

        assembly = cq.Assembly(name="thin_plate")
        plate = cq.Workplane("XY").box(self.length, self.width, self.thickness)
        assembly.add(plate)
        return assembly
