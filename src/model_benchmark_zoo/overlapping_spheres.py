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

        d = self.separation / 2
        r = self.radius

        assembly = cq.Assembly(name="overlapping_spheres")

        sphere1 = cq.Workplane().transformed(offset=(-d, 0, 0)).sphere(r)
        assembly.add(sphere1)

        sphere2_full = cq.Workplane().transformed(offset=(d, 0, 0)).sphere(r)
        sphere1_for_cut = cq.Workplane().transformed(offset=(-d, 0, 0)).sphere(r)
        sphere2 = sphere2_full.cut(sphere1_for_cut)
        assembly.add(sphere2)

        return assembly
