from .utils import BaseCommonGeometryObject
class Tetrahedral(BaseCommonGeometryObject):
    def __init__(self, length:float=1.,):
        self.length = length

    def csg_model(self, materials):
        import openmc

        coord_a = (0, 0, 0)
        coord_b = (self.length, 0, 0)
        coord_c = (0, self.length, 0)
        coord_d = (0, 0, self.length)

        plane1 = openmc.Plane.from_points(coord_b, coord_c, coord_d, boundary_type='vacuum')
        plane2 = openmc.Plane.from_points(coord_a, coord_c, coord_d, boundary_type='vacuum')
        plane3 = openmc.Plane.from_points(coord_a, coord_b, coord_d, boundary_type='vacuum')
        plane4 = openmc.Plane.from_points(coord_a, coord_b, coord_c, boundary_type='vacuum')

        region = -plane1 & +plane2 & -plane3 & +plane4

        cell = openmc.Cell(region=region)
        cell.fill = materials[0]
        my_materials = openmc.Materials(materials)
        geometry = openmc.Geometry([cell])
        model = openmc.Model(geometry=geometry, materials=my_materials)
        return model


    def cadquery_assembly(self):
        import cadquery as cq

        A = cq.Vector(0, 0, 0)
        B = cq.Vector(self.length, 0, 0)
        C = cq.Vector(0, self.length, 0)
        D = cq.Vector(0, 0, self.length)

        f1 = cq.Face.makeFromWires(cq.Wire.makePolygon([A, B, C, A]))
        f2 = cq.Face.makeFromWires(cq.Wire.makePolygon([A, B, D, A]))
        f3 = cq.Face.makeFromWires(cq.Wire.makePolygon([A, C, D, A]))
        f4 = cq.Face.makeFromWires(cq.Wire.makePolygon([B, C, D, B]))

        # Make a shell from the faces
        shell = cq.Shell.makeShell([f1, f2, f3, f4])

        # Convert shell to a solid
        result = cq.Solid.makeSolid(shell)

        assembly = cq.Assembly(name="tetrahedral")
        assembly.add(result)
        return assembly
