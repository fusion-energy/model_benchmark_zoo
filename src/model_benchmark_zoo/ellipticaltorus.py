from .utils import BaseCommonGeometryObject
class Ellipticaltorus(BaseCommonGeometryObject):
    def __init__(self, materials, major_radius=10, minor_radius1=2, minor_radius2=1):
        """
        input: minor_radius1 parallel to axis of revolution, minor_radius2 perpendicular to axis of revolution
        """
        self.materials = materials
        self.material_tags = [material.name for material in self.materials]
        self.major_radius = major_radius
        self.minor_radius1 = minor_radius1
        self.minor_radius2 = minor_radius2

    def csg_model(self, materials):
        import openmc

        surface = openmc.ZTorus(a=self.major_radius, b=self.minor_radius1, c=self.minor_radius2, boundary_type="vacuum")
        region = -surface
        cell = openmc.Cell(region=region)
        cell.fill = materials[0]
        materials = openmc.Materials(materials)
        geometry = openmc.Geometry([cell])
        model = openmc.Model(geometry=geometry, materials=materials)
        return model

    def cadquery_assembly(self):
        import cadquery as cq

        assembly = cq.Assembly(name="ellipticaltorus")
        ellipticaltorus1 = cq.Workplane("XZ", origin=(self.major_radius, 0, 0)).ellipse(self.minor_radius2, self.minor_radius1).revolve(180, (-self.major_radius,0,0), (-self.major_radius,1,0))
        ellipticaltorus2 = cq.Workplane("XZ", origin=(-self.major_radius, 0, 0)).ellipse(self.minor_radius2, self.minor_radius1).revolve(180, (self.major_radius,0,0), (self.major_radius,1,0))
        ellipticaltorus = ellipticaltorus1.union(ellipticaltorus2)        
        assembly.add(ellipticaltorus)
        return assembly
