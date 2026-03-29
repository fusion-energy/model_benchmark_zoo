from .utils import BaseCommonGeometryObject


class PebbleBedCell(BaseCommonGeometryObject):
    def __init__(self, box_width=20, sphere_radius=3, sphere_positions=None):
        if sphere_positions is None:
            sphere_positions = [(-4, -2, 0), (4, -2, 0), (0, 4, 0)]
        self.box_width = box_width
        self.sphere_radius = sphere_radius
        self.sphere_positions = sphere_positions

    def csg_model(self, materials):
        import openmc

        w = self.box_width
        r = self.sphere_radius

        box = openmc.model.RectangularParallelepiped(
            -w / 2, w / 2, -w / 2, w / 2, -w / 2, w / 2,
            boundary_type="vacuum",
        )

        spheres = []
        cells = []
        for i, (x, y, z) in enumerate(self.sphere_positions):
            sphere = openmc.Sphere(x0=x, y0=y, z0=z, r=r)
            spheres.append(sphere)
            cells.append(openmc.Cell(region=-sphere, fill=materials[i]))

        # Box region: inside box but outside all spheres
        box_region = -box
        for sphere in spheres:
            box_region = box_region & +sphere
        cells.append(
            openmc.Cell(region=box_region, fill=materials[len(self.sphere_positions)])
        )

        geometry = openmc.Geometry(cells)
        my_materials = openmc.Materials(materials)
        model = openmc.Model(geometry=geometry, materials=my_materials)
        return model

    def cadquery_assembly(self):
        import cadquery as cq

        w = self.box_width
        r = self.sphere_radius

        assembly = cq.Assembly(name="pebble_bed_cell")

        sphere_solids_for_cut = []
        for x, y, z in self.sphere_positions:
            sphere = cq.Workplane().transformed(offset=(x, y, z)).sphere(r)
            assembly.add(sphere)
            sphere_solids_for_cut.append(
                cq.Workplane().transformed(offset=(x, y, z)).sphere(r)
            )

        box = cq.Workplane("XY").box(w, w, w)
        for sphere in sphere_solids_for_cut:
            box = box.cut(sphere)
        assembly.add(box)

        return assembly
