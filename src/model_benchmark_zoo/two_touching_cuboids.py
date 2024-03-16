from .utils import BaseCommonGeometryObject

#     *----------*
#     |          |
#     |          |----*
#     |          |    |
#     |          |    |
#     |          |----*
#     |          |
#     *----------*

class TwoTouchingCuboids(BaseCommonGeometryObject):
    def __init__(self, width1=10, width2=4):
        self.width1 = width1
        self.width2 = width2

    def csg_model(self, materials):
        import openmc
        surface1 = openmc.ZPlane(z0=self.width1*0.5, boundary_type="vacuum")
        surface2 = openmc.ZPlane(z0=self.width1*-0.5, boundary_type="vacuum")
        surface3 = openmc.XPlane(x0=self.width1*0.5, boundary_type="vacuum")
        surface4 = openmc.XPlane(x0=self.width1*-0.5, boundary_type="vacuum")
        surface5 = openmc.YPlane(y0=self.width1*0.5)
        surface6 = openmc.YPlane(y0=self.width1*-0.5, boundary_type="vacuum")
        surface7 = openmc.YPlane(y0=self.width1*0.5+self.width2, boundary_type="vacuum")

        region1 = -surface1 & +surface2 & -surface3 & +surface4 & -surface5 & +surface6
        region2 = -surface1 & +surface2 & -surface3 & +surface4 & -surface7 & +surface5

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

        assembly = cq.Assembly(name="TwoTouchingCuboids")
        cuboid1 = cq.Workplane().box(self.width1, self.width1, self.width1)
        assembly.add(cuboid1)
        cuboid2 = cq.Workplane().moveTo(0.5*self.width1+ 0.5*self.width2).box(self.width2, self.width2, self.width2)
        assembly.add(cuboid2)
        return assembly
