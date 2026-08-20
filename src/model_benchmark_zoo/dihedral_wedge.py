import math

from .utils import BaseCommonGeometryObject

class DihedralWedge(BaseCommonGeometryObject):
    """A triangular prism whose two large faces meet at a chosen dihedral angle.

    A small angle between two planar faces is the textbook reason a conforming
    tetrahedral mesher fails to terminate: the sliver near the edge cannot be
    filled without either a very small element or a boundary the mesher is not
    allowed to move. ``angle`` is the variable to sweep, and it is the only thing
    that changes. The sharp edge stays on the z axis and the opposite face stays
    at x = ``length``, so a sweep moves the dihedral angle without also moving the
    extent of the solid, which is what :class:`Wedge` does when its base changes.

    :class:`Wedge` is one fixed instance of this, at about 17 degrees. The default
    here is 5 degrees, and the useful sweep runs down to 1 degree or below.
    """

    def __init__(self, angle=5, length=10, depth=10):
        if not 0 < angle < 90:
            raise ValueError("angle must satisfy 0 < angle < 90")
        if length <= 0 or depth <= 0:
            raise ValueError("length and depth must both be positive")
        self.angle = angle
        self.length = length
        self.depth = depth

    @property
    def far_height(self):
        """Thickness of the wedge at the face opposite the sharp edge."""
        return self.length * math.tan(math.radians(self.angle))

    def analytic_volumes(self):
        """Exact volume of the triangular prism, half the far face times the depth."""
        return (
            self.length * self.far_height / 2 * self.depth,
        )

    def _csg_model(self, materials):
        import openmc

        length = self.length
        depth = self.depth
        slope = math.tan(math.radians(self.angle))

        x_edge = openmc.XPlane(x0=0, boundary_type="vacuum")
        x_far = openmc.XPlane(x0=length, boundary_type="vacuum")
        y_bottom = openmc.YPlane(y0=0, boundary_type="vacuum")
        z_front = openmc.ZPlane(z0=-depth / 2, boundary_type="vacuum")
        z_back = openmc.ZPlane(z0=depth / 2, boundary_type="vacuum")

        # Inclined face y = x * tan(angle), which meets the y = 0 face along the
        # z axis at the requested angle. The material is on the negative side.
        inclined = openmc.Plane(a=-slope, b=1.0, c=0.0, d=0.0,
                                boundary_type="vacuum")

        region = (
            +x_edge & -x_far & +y_bottom & -inclined & +z_front & -z_back
        )

        cell = openmc.Cell(region=region, fill=materials[0])

        geometry = openmc.Geometry([cell])
        my_materials = openmc.Materials(materials)
        model = openmc.Model(geometry=geometry, materials=my_materials)
        return model

    def cadquery_assembly(self):
        import cadquery as cq

        length = self.length
        depth = self.depth

        assembly = cq.Assembly(name="dihedral_wedge")
        wedge = (
            cq.Workplane("XY")
            .transformed(offset=(0, 0, -depth / 2))
            .moveTo(0, 0)
            .lineTo(length, 0)
            .lineTo(length, self.far_height)
            .close()
            .extrude(depth)
        )
        assembly.add(wedge)
        return assembly
