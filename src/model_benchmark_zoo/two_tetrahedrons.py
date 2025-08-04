from .utils import BaseCommonGeometryObject


class TwoTetrahedrons(BaseCommonGeometryObject):
    """
    This geometry is composed of two tetrahedrons that share a face.
    It is based on the single Tetrahedral geometry.
    """

    def __init__(
        self,
        length: float = 1.0,
    ):
        self.length = length

    def csg_model(self, materials):
        """
        Creates a CSG model of two tetrahedrons sharing a face.

        Args:
            materials (list of openmc.Material): A list of two materials,
                one for each tetrahedron.
        """
        import openmc

        # Tet 1 planes
        plane_x0 = openmc.XPlane(0)
        plane_y0 = openmc.YPlane(0, boundary_type="vacuum")
        plane_z0 = openmc.ZPlane(0, boundary_type="vacuum")
        plane_1 = openmc.Plane(a=1, b=1, c=1, d=self.length, boundary_type="vacuum")

        # Tet 2 planes
        plane_2 = openmc.Plane(a=-1, b=1, c=1, d=self.length, boundary_type="vacuum")

        # Tet 1 region
        region1 = +plane_x0 & +plane_y0 & +plane_z0 & -plane_1

        # Tet 2 region
        region2 = -plane_x0 & +plane_y0 & +plane_z0 & -plane_2

        cell1 = openmc.Cell(region=region1)
        cell1.fill = materials[0]
        cell2 = openmc.Cell(region=region2)
        cell2.fill = materials[1]

        my_materials = openmc.Materials(materials)
        geometry = openmc.Geometry([cell1, cell2])
        model = openmc.Model(geometry=geometry, materials=my_materials)
        return model

    def cadquery_assembly(self):
        """
        Creates a CAD model of two tetrahedrons sharing a face.
        """
        import cadquery as cq

        # Vertices for the first tetrahedron
        A = cq.Vector(0, 0, 0)
        B = cq.Vector(self.length, 0, 0)
        C = cq.Vector(0, self.length, 0)
        D = cq.Vector(0, 0, self.length)

        # Vertices for the second tetrahedron
        B_prime = cq.Vector(-self.length, 0, 0)

        # Create faces for the first tetrahedron
        f1_1 = cq.Face.makeFromWires(cq.Wire.makePolygon([A, B, C, A]))
        f1_2 = cq.Face.makeFromWires(cq.Wire.makePolygon([A, B, D, A]))
        f1_3 = cq.Face.makeFromWires(cq.Wire.makePolygon([A, C, D, A]))
        f1_4 = cq.Face.makeFromWires(cq.Wire.makePolygon([B, C, D, B]))
        shell1 = cq.Shell.makeShell([f1_1, f1_2, f1_3, f1_4])
        solid1 = cq.Solid.makeSolid(shell1)

        # Create faces for the second tetrahedron
        f2_1 = cq.Face.makeFromWires(cq.Wire.makePolygon([A, B_prime, C, A]))
        f2_2 = cq.Face.makeFromWires(cq.Wire.makePolygon([A, B_prime, D, A]))
        f2_3 = cq.Face.makeFromWires(cq.Wire.makePolygon([A, C, D, A]))
        f2_4 = cq.Face.makeFromWires(cq.Wire.makePolygon([B_prime, C, D, B_prime]))
        shell2 = cq.Shell.makeShell([f2_1, f2_2, f2_3, f2_4])
        solid2 = cq.Solid.makeSolid(shell2)

        assembly = cq.Assembly(name="two_tetrahedrons")
        assembly.add(solid1)
        assembly.add(solid2)
        return assembly
