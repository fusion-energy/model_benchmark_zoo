from .utils import BaseCommonGeometryObject
class NestedCylinder(BaseCommonGeometryObject):
    def __init__(self, height1=15, height2=8, radius1=15, radius2=8):
        
        if height1<=height2:
            raise ValueError('height1 should be greater than height2')
        if radius1<=radius2:
            raise ValueError('radius1 should be greater than radius2')

        self.height1 = height1
        self.height2 = height2
        self.radius1 = radius1
        self.radius2 = radius2

    def csg_model(self, materials):
        import openmc
        
        surface_1 = openmc.ZCylinder(x0=0.0, y0=0.0, r=self.radius1, boundary_type="vacuum")
        surface_2 = openmc.ZPlane(z0=0.5*self.height1, boundary_type="vacuum")
        surface_3 = openmc.ZPlane(z0=-0.5*self.height1, boundary_type="vacuum")
    
        surface_3 = openmc.ZCylinder(x0=0.0, y0=0.0, r=self.radius2, boundary_type="vacuum")
        surface_4 = openmc.ZPlane(z0=0.5*self.height2, boundary_type="vacuum")
        surface_5 = openmc.ZPlane(z0=-0.5*self.height2, boundary_type="vacuum")
    
        region_1 = -surface_1 & -surface_2 & +surface_3
        region_2 = -surface_3 & -surface_4 & +surface_5

        cell_1 = openmc.Cell(region=region_1 & ~ region_2, fill=materials[0])
        cell_2 = openmc.Cell(region=region_2, fill=materials[1])

        geometry = openmc.Geometry([cell_1, cell_2])
        materials = openmc.Materials(materials)
        model = openmc.Model(geometry=geometry, materials=materials)
        return model

    def cadquery_assembly(self):
        import cadquery as cq

        assembly = cq.Assembly(name="cylinder")
        cylinder2 = cq.Workplane("XY", origin=(0, 0, 0)).circle(self.radius2).extrude(self.height2, both=True)
        cylinder1 = cq.Workplane("XY", origin=(0, 0, 0)).circle(self.radius1).extrude(self.height1, both=True).cut(cylinder2)
        assembly.add(cylinder1)
        assembly.add(cylinder2)
        return assembly
