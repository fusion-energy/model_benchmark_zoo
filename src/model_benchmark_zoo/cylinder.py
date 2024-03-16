from .utils import BaseCommonGeometryObject
class Cylinder(BaseCommonGeometryObject):
    def __init__(self, materials, radius=1, height=100):
        self.materials = materials
        self.material_tags = [material.name for material in self.materials]
        self.radius = radius
        self.height = height

    def csg_model(self, materials):
        import openmc

        surface_1 = openmc.ZCylinder(x0=0.0, y0=0.0, r=self.radius, boundary_type="vacuum")
        surface_2 = openmc.ZPlane(z0=0.5*self.height, boundary_type="vacuum")
        surface_3 = openmc.ZPlane(z0=-0.5*self.height, boundary_type="vacuum")
    
        region = -surface_1 & -surface_2 & +surface_3
        cell = openmc.Cell(region=region)
        cell.fill = materials[0]
        materials = openmc.Materials(materials)
        geometry = openmc.Geometry([cell])
        model = openmc.Model(geometry=geometry, materials=materials)
        return model
    
    def cadquery_assembly(self):
        import cadquery as cq

        assembly = cq.Assembly(name="cylinder")
        cylinder = cq.Workplane("XY", origin=(0, 0, 0)).circle(self.radius).extrude(self.height, both=True)
        assembly.add(cylinder)
        return assembly
