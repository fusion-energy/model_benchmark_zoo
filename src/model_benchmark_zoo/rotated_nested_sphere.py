import math

from .utils import BaseCommonGeometryObject


class RotatedNestedSphere(BaseCommonGeometryObject):
    """A sphere inside a spherical shell whose poles do not line up with its own.

    The geometry is exactly :class:`NestedSphere`. The only difference is that
    the shell is rotated about an axis through the centre after it is built, so
    the poles and the seam of its inner spherical face sit somewhere other than
    the poles and seam of the inner sphere. Rotating a sphere about its centre
    does not move any of its surface, so the volumes and the CSG model are the
    same as for the unrotated case.

    Two solids that share a spherical face nearly always come from different
    places in real CAD: a part imported from one tool and a cavity cut in
    another, or a component placed into an assembly at an angle. Nothing makes
    their parametrisations agree, and the zoo had no case where they did not.
    In :class:`NestedSphere` and :class:`SphereInBox` the shared face comes from
    the same ``sphere()`` call on both sides, so its poles and seam line up by
    construction.

    When OCCT imprints the two solids it keeps one copy of the shared spherical
    face, and the other solid's seam and pole edges are left lying on it as
    internal edges that no other face uses. A mesher that triangulates the
    shared face then has to respect an open wire running from pole to pole
    across the middle of the surface, which is not something a single closed
    sphere ever asks of it. Faceting the shared face badly shows up directly as
    a wrong volume for the inner sphere and a matching error in the shell.

    The default of 11 degrees about y is not special geometrically, any
    rotation that moves the poles does the same thing. A rotation about z, the
    pole axis, leaves the poles where they were and so does not exercise it,
    and neither does a half turn about x, which swaps the poles over.

    Args:
        radius1: radius of the inner sphere.
        radius2: thickness of the shell around it.
        rotation_angle: angle in degrees the shell is rotated by.
        rotation_axis: direction of the axis through the centre the shell is
            rotated about.
    """

    def __init__(self, radius1=10, radius2=5, rotation_angle=11, rotation_axis=(0, 1, 0)):
        self.radius1 = radius1
        self.radius2 = radius2
        self.rotation_angle = rotation_angle
        self.rotation_axis = rotation_axis

    def analytic_volumes(self):
        """Exact volume of the inner sphere and of the shell on it."""
        return (
            4 / 3 * math.pi * self.radius1 ** 3,
            4 / 3 * math.pi * (self.radius1 + self.radius2) ** 3
            - 4 / 3 * math.pi * self.radius1 ** 3,
        )

    def _csg_model(self, materials):
        import openmc

        # The rotation leaves every surface where it was, so the CSG model is
        # the same as the one for NestedSphere.
        surface1 = openmc.Sphere(r=self.radius1)
        surface2 = openmc.Sphere(r=self.radius1 + self.radius2, boundary_type="vacuum")
        region1 = -surface1
        region2 = +surface1 & -surface2
        cell1 = openmc.Cell(region=region1)
        cell1.fill = materials[0]
        cell2 = openmc.Cell(region=region2)
        cell2.fill = materials[1]
        geometry = openmc.Geometry([cell1, cell2])
        my_materials = openmc.Materials(materials)
        model = openmc.Model(geometry=geometry, materials=my_materials)
        return model

    def cadquery_assembly(self):
        import cadquery as cq

        assembly = cq.Assembly(name="rotated_nested_sphere")
        sphere1 = cq.Workplane().sphere(self.radius1)
        sphere2 = (
            cq.Workplane()
            .sphere(self.radius1 + self.radius2)
            .cut(cq.Workplane().sphere(self.radius1))
            .rotate((0, 0, 0), self.rotation_axis, self.rotation_angle)
        )
        assembly.add(sphere1)
        assembly.add(sphere2)
        return assembly
