from .utils import BaseCommonGeometryObject
class NestedSphere(BaseCommonGeometryObject):
    def __init__(self, radius1=10, radius2=5):
        self.radius1 = radius1
        self.radius2 = radius2

    def csg_model(self, materials):
        import openmc
        
        surface1 = openmc.Sphere(r=self.radius1)
        surface2 = openmc.Sphere(r=self.radius1+self.radius2, boundary_type="vacuum")
        region1 = -surface1
        region2 = +surface1 & -surface2
        cell1 = openmc.Cell(region=region1)
        cell1.fill = materials[0]
        cell2 = openmc.Cell(region=region2)
        cell2.fill = materials[1]
        geometry = openmc.Geometry([cell1, cell2])
        my_materials = openmc.Materials(materials)
        model = openmc.Model(geometry=geometry, materials=my_materials)
        return model

    def cadquery_assembly(self):
        import cadquery as cq

        assembly = cq.Assembly(name="nestedshpere")
        sphere1 = cq.Workplane().sphere(self.radius1)
        sphere2 = cq.Workplane().sphere(self.radius1 + self.radius2).cut(sphere1)
        assembly.add(sphere1)
        assembly.add(sphere2)
        return assembly
