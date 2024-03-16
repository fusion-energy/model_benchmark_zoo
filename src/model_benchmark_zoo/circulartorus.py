from .utils import BaseCommonGeometryObject
class Circulartorus(BaseCommonGeometryObject):
    def __init__(self, major_radius=10, minor_radius=1):
        self.major_radius = major_radius
        self.minor_radius = minor_radius

    def csg_model(self, materials):
        import openmc

        surface = openmc.ZTorus(
            a=self.major_radius,
            b=self.minor_radius,
            c=self.minor_radius,
            boundary_type="vacuum"
        )
        region = -surface
        cell = openmc.Cell(region=region)
        cell.fill = materials[0]
        geometry = openmc.Geometry([cell])
        materials = openmc.Materials(materials)
        model = openmc.Model(geometry=geometry, materials=materials)
        return model

    def cadquery_assembly(self):
        import cadquery as cq

        assembly = cq.Assembly(name="circulartorus")
        circulartorus = cq.Solid.makeTorus(self.major_radius, self.minor_radius)
        assembly.add(circulartorus)
        return assembly