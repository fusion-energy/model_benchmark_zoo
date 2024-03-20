
from .utils import BaseCommonGeometryObject

class SimpleTokamak(BaseCommonGeometryObject):
    def __init__(
            self,
            radius=500,
            blanket_thicknesses=100,
            center_column_thicknesses=150,
            center_column_extent_beyond_blanket=10,
        ):
        self.radius = radius
        self.blanket_thicknesses = blanket_thicknesses
        self.center_column_thicknesses = center_column_thicknesses
        self.center_column_extent_beyond_blanket = center_column_extent_beyond_blanket

    def csg_model(self, materials):
        import openmc
        
        center_column_height = (self.radius + self.blanket_thicknesses + self.center_column_extent_beyond_blanket)*2

        surface_inner_wall = openmc.Sphere(r=self.radius)
        surface_outer_wall = openmc.Sphere(r=self.radius + self.blanket_thicknesses)
        surface_center_cylinder = openmc.ZCylinder(r=self.center_column_thicknesses)
        surface_top_cy = openmc.ZPlane(z0=center_column_height/2, boundary_type='vacuum')
        surface_bot_cy = openmc.ZPlane(z0=-center_column_height/2, boundary_type='vacuum')
        outer_surface = openmc.ZCylinder(r=self.radius + self.blanket_thicknesses, boundary_type='vacuum')
        
        region1 = -surface_inner_wall & +surface_center_cylinder  # plasma
        region2 = +surface_inner_wall & -surface_outer_wall & +surface_center_cylinder # blanket
        region3 = -surface_top_cy & +surface_bot_cy & -surface_center_cylinder  # center column
        region4 = +surface_outer_wall & -surface_top_cy & +surface_bot_cy & +surface_center_cylinder & -outer_surface  # outer vessel

        cell1 = openmc.Cell(region=region1) # plasma
        cell2 = openmc.Cell(region=region2) # blanket
        cell2.fill = materials[0]
        cell3 = openmc.Cell(region=region3) # center column
        cell3.fill = materials[1]
        cell4 = openmc.Cell(region=region4) # outer vessel

        geometry = openmc.Geometry([cell1, cell2, cell3, cell4])
        materials = openmc.Materials([materials[0], materials[1]])
        model = openmc.Model(geometry=geometry, materials=materials)
        return model

    def cadquery_assembly(self):
        import cadquery as cq

        assembly = cq.Assembly(name="simpletokamak")

        # sphere_envelope = cq.Workplane().sphere(self.radius + self.blanket_thicknesses)

        center_column_height = self.radius + self.blanket_thicknesses + self.center_column_extent_beyond_blanket

        sphere1 = cq.Workplane().sphere(self.radius)
        sphere2 = cq.Workplane().sphere(self.radius + self.blanket_thicknesses)
        
        center_column = cq.Workplane("XY").circle(self.center_column_thicknesses).extrude(center_column_height, both=True)
        
        sphere2 = sphere2.cut(sphere1).cut(center_column)

        assembly.add(sphere2)
        assembly.add(center_column)
        return assembly
