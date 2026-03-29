from .utils import BaseCommonGeometryObject


class OverlappingSpheres(BaseCommonGeometryObject):
    def __init__(self, radius=5, separation=6):

        if separation >= 2 * radius:
            raise ValueError("separation must be less than 2*radius for spheres to overlap")

        self.radius = radius
        self.separation = separation

    def csg_model(self, materials):
        import openmc

        d = self.separation / 2
        r = self.radius

        sphere1 = openmc.Sphere(x0=-d, r=r)
        sphere2 = openmc.Sphere(x0=d, r=r)
        bounding = openmc.Sphere(r=r + d + 1, boundary_type="vacuum")

        # Sphere 1 (including overlap region): mat1
        region1 = -sphere1
        # Sphere 2 minus sphere 1: mat2
        region2 = -sphere2 & +sphere1
        # Void outside both
        region_void = -bounding & +sphere1 & +sphere2

        cell1 = openmc.Cell(region=region1, fill=materials[0])
        cell2 = openmc.Cell(region=region2, fill=materials[1])
        cell3 = openmc.Cell(region=region_void)

        geometry = openmc.Geometry([cell1, cell2, cell3])
        my_materials = openmc.Materials(materials)
        model = openmc.Model(geometry=geometry, materials=my_materials)
        return model

    def cadquery_assembly(self):
        import cadquery as cq
        from OCP.BRepPrimAPI import BRepPrimAPI_MakeSphere
        from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut
        from OCP.gp import gp_Pnt

        d = self.separation / 2
        r = self.radius

        assembly = cq.Assembly(name="overlapping_spheres")

        sphere1_shape = BRepPrimAPI_MakeSphere(gp_Pnt(-d, 0, 0), r).Shape()
        sphere2_shape = BRepPrimAPI_MakeSphere(gp_Pnt(d, 0, 0), r).Shape()

        assembly.add(cq.Workplane().add(cq.Solid(sphere1_shape)))

        crescent_shape = BRepAlgoAPI_Cut(sphere2_shape, sphere1_shape).Shape()
        assembly.add(cq.Workplane().add(cq.Solid(crescent_shape)))

        return assembly
