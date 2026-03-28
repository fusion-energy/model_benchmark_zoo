from .utils import BaseCommonGeometryObject

class ThinWalledSphere(BaseCommonGeometryObject):
    def __init__(self, outer_radius=5, inner_radius=4.5):
        if inner_radius >= outer_radius:
            raise ValueError('inner_radius should be less than outer_radius')
        self.outer_radius = outer_radius
        self.inner_radius = inner_radius

    def csg_model(self, materials):
        import openmc

        outer = openmc.Sphere(r=self.outer_radius, boundary_type="vacuum")
        inner = openmc.Sphere(r=self.inner_radius)

        region_wall = -outer & +inner
        region_void = -inner

        cell1 = openmc.Cell(region=region_wall, fill=materials[0])
        cell2 = openmc.Cell(region=region_void)

        geometry = openmc.Geometry([cell1, cell2])
        my_materials = openmc.Materials(materials)
        model = openmc.Model(geometry=geometry, materials=my_materials)
        return model

    def cadquery_assembly(self):
        import cadquery as cq

        assembly = cq.Assembly(name="thin_walled_sphere")
        outer = cq.Workplane().sphere(self.outer_radius)
        inner = cq.Workplane().sphere(self.inner_radius)
        shell = outer.cut(inner)
        assembly.add(shell)
        return assembly
