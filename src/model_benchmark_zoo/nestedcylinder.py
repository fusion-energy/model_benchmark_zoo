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

        outer_cyl = openmc.ZCylinder(x0=0.0, y0=0.0, r=self.radius1, boundary_type="vacuum")
        outer_top = openmc.ZPlane(z0=0.5*self.height1, boundary_type="vacuum")
        outer_bot = openmc.ZPlane(z0=-0.5*self.height1, boundary_type="vacuum")

        inner_cyl = openmc.ZCylinder(x0=0.0, y0=0.0, r=self.radius2)
        inner_top = openmc.ZPlane(z0=0.5*self.height2)
        inner_bot = openmc.ZPlane(z0=-0.5*self.height2)

        region_inner = -inner_cyl & -inner_top & +inner_bot
        region_outer = (-outer_cyl & -outer_top & +outer_bot) & ~region_inner

        cell_1 = openmc.Cell(region=region_outer, fill=materials[0])
        cell_2 = openmc.Cell(region=region_inner, fill=materials[1])

        geometry = openmc.Geometry([cell_1, cell_2])
        my_materials = openmc.Materials(materials)
        model = openmc.Model(geometry=geometry, materials=my_materials)
        return model

    def cadquery_assembly(self):
        import cadquery as cq

        assembly = cq.Assembly(name="cylinder")
        cylinder2 = cq.Workplane("XY").cylinder(self.height2, self.radius2)
        cylinder1 = cq.Workplane("XY").cylinder(self.height1, self.radius1).cut(cylinder2)
        assembly.add(cylinder1)
        assembly.add(cylinder2)
        return assembly
