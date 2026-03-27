from .utils import BaseCommonGeometryObject

class SphereInBox(BaseCommonGeometryObject):
    def __init__(self, box_width=12, sphere_radius=4):
        self.box_width = box_width
        self.sphere_radius = sphere_radius

    def csg_model(self, materials):
        import openmc

        w = self.box_width
        r = self.sphere_radius

        box = openmc.model.RectangularParallelepiped(
            -w / 2, w / 2, -w / 2, w / 2, -w / 2, w / 2,
            boundary_type="vacuum"
        )
        sphere = openmc.Sphere(r=r)

        region_sphere = -sphere
        region_box = -box & +sphere

        cell_sphere = openmc.Cell(region=region_sphere, fill=materials[0])
        cell_box = openmc.Cell(region=region_box, fill=materials[1])

        geometry = openmc.Geometry([cell_sphere, cell_box])
        my_materials = openmc.Materials(materials)
        model = openmc.Model(geometry=geometry, materials=my_materials)
        return model

    def cadquery_assembly(self):
        import cadquery as cq

        w = self.box_width
        r = self.sphere_radius

        assembly = cq.Assembly(name="sphere_in_box")

        sphere = cq.Workplane().sphere(r)
        box = cq.Workplane("XY").box(w, w, w)
        box_shell = box.cut(sphere)

        assembly.add(sphere)
        assembly.add(box_shell)
        return assembly
