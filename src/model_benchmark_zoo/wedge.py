from .utils import BaseCommonGeometryObject

class Wedge(BaseCommonGeometryObject):
    def __init__(self, base=3, height=10, depth=10):
        self.base = base
        self.height = height
        self.depth = depth

    def csg_model(self, materials):
        import openmc

        b = self.base
        h = self.height
        d = self.depth

        x_left = openmc.XPlane(x0=0, boundary_type="vacuum")
        y_bottom = openmc.YPlane(y0=0, boundary_type="vacuum")
        z_front = openmc.ZPlane(z0=-d / 2, boundary_type="vacuum")
        z_back = openmc.ZPlane(z0=d / 2, boundary_type="vacuum")

        # Hypotenuse plane from (b, 0) to (0, h): h*x + b*y = b*h
        hypotenuse = openmc.Plane(a=h, b=b, c=0, d=b * h, boundary_type="vacuum")

        region = +x_left & +y_bottom & -hypotenuse & +z_front & -z_back

        cell = openmc.Cell(region=region, fill=materials[0])

        geometry = openmc.Geometry([cell])
        my_materials = openmc.Materials(materials)
        model = openmc.Model(geometry=geometry, materials=my_materials)
        return model

    def cadquery_assembly(self):
        import cadquery as cq

        b = self.base
        h = self.height
        d = self.depth

        assembly = cq.Assembly(name="wedge")
        wedge = (
            cq.Workplane("XY")
            .transformed(offset=(0, 0, -d / 2))
            .moveTo(0, 0)
            .lineTo(b, 0)
            .lineTo(0, h)
            .close()
            .extrude(d)
        )
        assembly.add(wedge)
        return assembly
