from .utils import BaseCommonGeometryObject

class ConcentricCylinders(BaseCommonGeometryObject):
    def __init__(self, height=20, radii=None):
        if radii is None:
            radii = [2, 4, 6]
        if len(radii) < 2:
            raise ValueError('radii must have at least 2 values')
        if radii != sorted(radii):
            raise ValueError('radii must be in ascending order')
        self.height = height
        self.radii = radii

    def csg_model(self, materials):
        import openmc

        h = self.height
        z_top = openmc.ZPlane(z0=h / 2, boundary_type="vacuum")
        z_bot = openmc.ZPlane(z0=-h / 2, boundary_type="vacuum")

        cylinders = []
        for i, r in enumerate(self.radii):
            bt = "vacuum" if i == len(self.radii) - 1 else "transmission"
            cylinders.append(openmc.ZCylinder(r=r, boundary_type=bt))

        cells = []
        # Innermost solid cylinder
        region0 = -cylinders[0] & +z_bot & -z_top
        cells.append(openmc.Cell(region=region0, fill=materials[0]))

        # Cylindrical shells
        for i in range(1, len(self.radii)):
            region = +cylinders[i - 1] & -cylinders[i] & +z_bot & -z_top
            cells.append(openmc.Cell(region=region, fill=materials[i]))

        geometry = openmc.Geometry(cells)
        my_materials = openmc.Materials(materials)
        model = openmc.Model(geometry=geometry, materials=my_materials)
        return model

    def cadquery_assembly(self):
        import cadquery as cq

        assembly = cq.Assembly(name="concentric_cylinders")
        h = self.height

        # Build from inside out; each shell is outer minus inner
        prev = None
        for r in self.radii:
            cyl = cq.Workplane("XY").cylinder(h, r)
            if prev is not None:
                shell = cyl.cut(prev)
                assembly.add(shell)
            else:
                assembly.add(cyl)
            prev = cq.Workplane("XY").cylinder(h, r)

        return assembly
