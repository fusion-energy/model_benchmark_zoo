
from .utils import BaseCommonGeometryObject

class SimpleTokamak(BaseCommonGeometryObject):
    def __init__(self, radius=500, blanket_thicknesses=100, center_column_thicknesses=50):
        self.radius = radius
        self.blanket_thicknesses = blanket_thicknesses
        self.center_column_thicknesses = center_column_thicknesses

    def csg_model(self, materials):
        import openmc
        
        surface1 = openmc.Sphere(r=self.radius)
        surface2 = openmc.Sphere(r=self.radius + self.blanket_thicknesses, boundary_type="vacuum")
        surface3 = openmc.ZCylinder(r=self.center_column_thicknesses)
        
        region1 = -surface1 & +surface3  # plasma
        region2 = +surface1 & -surface2  # blanket
        region3 = -surface2 & -surface3  # center column

        cell1 = openmc.Cell(region=region1)
        cell2 = openmc.Cell(region=region2)
        cell2.fill = materials[0]
        cell3 = openmc.Cell(region=region3)
        cell3.fill = materials[1]

        geometry = openmc.Geometry([cell1, cell2, cell3])
        materials = openmc.Materials([materials[0], materials[1]])
        model = openmc.Model(geometry=geometry, materials=materials)
        return model

    def cadquery_assembly(self):
        import cadquery as cq

        assembly = cq.Assembly(name="simpletokamak")

        sphere_envelope = cq.Workplane().sphere(self.radius + self.blanket_thicknesses)

        center_column = cq.Workplane("XY").circle(self.radius).extrude(self.radius+self.blanket_thicknesses).intersect(sphere_envelope)

        sphere1 = cq.Workplane().sphere(self.radius)
        sphere2 = cq.Workplane().sphere(self.radius + self.blanket_thicknesses).cut(sphere1).cut(center_column)

        assembly.add(sphere2)
        assembly.add(center_column)
        return assembly
