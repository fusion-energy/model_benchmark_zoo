from .utils import BaseCommonGeometryObject

class EllipticCylinder(BaseCommonGeometryObject):
    def __init__(self, a=8, b=5, height=15):
        self.a = a
        self.b = b
        self.height = height

    def csg_model(self, materials):
        import openmc

        # Elliptic cylinder: x²/a² + y²/b² = 1
        # openmc.Quadric: Ax² + By² + Cz² + Dxy + Eyz + Fxz + Gx + Hy + Jz + K = 0
        # So: (1/a²)x² + (1/b²)y² + (-1) = 0
        quadric = openmc.Quadric(
            a=1.0 / self.a**2,
            b=1.0 / self.b**2,
            c=0,
            d=0,
            e=0,
            f=0,
            g=0,
            h=0,
            j=0,
            k=-1,
            boundary_type="vacuum",
        )

        z_top = openmc.ZPlane(z0=0.5 * self.height, boundary_type="vacuum")
        z_bot = openmc.ZPlane(z0=-0.5 * self.height, boundary_type="vacuum")

        region = -quadric & +z_bot & -z_top
        cell = openmc.Cell(region=region)
        cell.fill = materials[0]
        geometry = openmc.Geometry([cell])
        my_materials = openmc.Materials(materials)
        model = openmc.Model(geometry=geometry, materials=my_materials)
        return model

    def cadquery_assembly(self):
        import cadquery as cq

        assembly = cq.Assembly(name="elliptic_cylinder")
        ellipse = cq.Workplane("XY").ellipse(self.a, self.b).extrude(self.height / 2, both=True)
        assembly.add(ellipse)
        return assembly
