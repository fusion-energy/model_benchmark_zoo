from .utils import BaseCommonGeometryObject

class CubicLattice(BaseCommonGeometryObject):
    def __init__(self, box_width=20, sphere_radius=3):
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

        spheres = []
        cells = []
        for dx in [-1, 1]:
            for dy in [-1, 1]:
                for dz in [-1, 1]:
                    s = openmc.Sphere(x0=dx * w / 4, y0=dy * w / 4, z0=dz * w / 4, r=r)
                    spheres.append(s)
                    cells.append(openmc.Cell(region=-s, fill=materials[0]))

        # Matrix: inside box, outside all spheres
        matrix_region = -box
        for s in spheres:
            matrix_region = matrix_region & +s
        cells.append(openmc.Cell(region=matrix_region, fill=materials[1]))

        geometry = openmc.Geometry(cells)
        my_materials = openmc.Materials(materials)
        model = openmc.Model(geometry=geometry, materials=my_materials)
        return model

    def cadquery_assembly(self):
        import cadquery as cq

        assembly = cq.Assembly(name="cubic_lattice")

        w = self.box_width
        r = self.sphere_radius

        sphere_solids = []
        for dx in [-1, 1]:
            for dy in [-1, 1]:
                for dz in [-1, 1]:
                    x, y, z = dx * w / 4, dy * w / 4, dz * w / 4
                    sphere = cq.Workplane().transformed(offset=(x, y, z)).sphere(r)
                    assembly.add(sphere)
                    sphere_solids.append(
                        cq.Workplane().transformed(offset=(x, y, z)).sphere(r)
                    )

        box = cq.Workplane("XY").box(w, w, w)
        for s in sphere_solids:
            box = box.cut(s)
        assembly.add(box)

        return assembly
