from .utils import BaseCommonGeometryObject

class Oktavian(BaseCommonGeometryObject):

    def csg_model(self, materials):
        import openmc
    
        # surfaces
        surf_1 = openmc.XCylinder(surface_id=1, y0=0.0, z0=0.0, r=5.55)
        surf_2 = openmc.XCylinder(surface_id=2, y0=0.0, z0=0.0, r=5.75)
        surf_3 = openmc.Sphere(surface_id=3, x0=0.0, y0=0.0, z0=0.0, r=10.0)
        surf_4 = openmc.Sphere(surface_id=4, x0=0.0, y0=0.0, z0=0.0, r=10.2)
        surf_5 = openmc.Sphere(surface_id=5, x0=0.0, y0=0.0, z0=0.0, r=19.75)
        surf_6 = openmc.Sphere(surface_id=6, x0=0.0, y0=0.0, z0=0.0, r=19.95)
        surf_7 = openmc.Sphere(surface_id=7, x0=0.0, y0=0.0, z0=0.0, r=100.0, boundary_type="vacuum")
        surf_8 = openmc.XPlane(surface_id=8, x0=8.32)

        # regions
        region_1 = (-surf_3 & -surf_8) | (+surf_8 & -surf_1 & -surf_6)
        region_2 = (+surf_3 & -surf_4 & -surf_8) | (+surf_8 & +surf_1 & -surf_2 & -surf_6)
        region_3 = (+surf_4 & -surf_5 & -surf_8) | (+surf_8 & +surf_2 & -surf_5)
        region_4 = (+surf_5 & -surf_6 & -surf_8) | (+surf_8 & +surf_2 & +surf_5 & -surf_6)
        region_5 = +surf_6 & -surf_7

        # cells
        cell_1 = openmc.Cell(cell_id=1, region=region_1, fill=None)
        cell_2 = openmc.Cell(cell_id=2, region=region_2, fill=materials[1])
        cell_3 = openmc.Cell(cell_id=3, region=region_3, fill=materials[0])
        cell_4 = openmc.Cell(cell_id=4, region=region_4, fill=materials[1])
        cell_5 = openmc.Cell(cell_id=5, region=region_5, fill=None)

        # create geometry instance
        geometry = openmc.Geometry([cell_1, cell_2, cell_3, cell_4, cell_5])
        my_materials = openmc.Materials([materials[0], materials[1]])
        model = openmc.Model(geometry=geometry, materials=my_materials)
        return model

    def cadquery_assembly(self):
        import cadquery as cq
    
        assembly = cq.Assembly(name="oktavian")

        sphere1_radius = 10
        cylinder_radius = 5.55
        cylinder2_radius = cylinder_radius+0.2
        sphere2_radius = sphere1_radius+0.2
        sphere3_radius=sphere2_radius+9.55
        sphere4_radius=sphere3_radius+0.2

        sphere1 = cq.Workplane('XY').sphere(sphere1_radius)
        sphere2 = cq.Workplane('XY').sphere(sphere2_radius)
        sphere3 = cq.Workplane('XY').sphere(sphere3_radius)
        sphere4 = cq.Workplane('XY').sphere(sphere4_radius)

        cylinder1 = cq.Workplane('XY').cylinder(radius=cylinder_radius, height=300, centered=(0.5*cylinder_radius,10,0))
        cylinder2 = cq.Workplane('XY').cylinder(radius=cylinder2_radius, height=300, centered=(0.5*cylinder2_radius,10,0))

        cylinder2 = cylinder2.intersect(sphere4)
        inner_void = sphere1.union(cylinder1)
        inner_wall_sp = sphere2.cut(sphere1).cut(cylinder1)
        inner_wall_cy = cylinder2.cut(cylinder1)
        inner_wall = inner_wall_sp.union(inner_wall_cy)
        mid_wall = sphere3.cut(sphere2).cut(cylinder2)
        outer_wall =  sphere4.cut(sphere3).cut(cylinder2)
        wall = outer_wall.union(inner_wall).cut(sphere1)

        assembly.add(mid_wall)
        assembly.add(wall)
        return assembly
