"""Models whose CAD faces are B-splines rather than analytic surfaces.

Real inputs, such as the STEP files GEOUNED writes, are NURBS heavy, but no face of
any model in the zoo was a B-spline: every curved one is a sphere, cylinder, cone,
torus, surface of revolution or surface of extrusion. Even TruncatedCone, which is
built by lofting between two different circles, comes back with an analytic conical
face because OCCT recognises what the loft produced.

The two models here are converted to B-splines after being built, with
``BRepBuilderAPI_NurbsConvert``. That keeps the geometry exact, since a rational
B-spline represents a conic section exactly, so each one still has a CSG equivalent
that is right to the last digit rather than to a fitting tolerance. A shape whose
surface is genuinely arbitrary, a loft between a circle and a square say, has no CSG
equivalent at all and so cannot be compared the way this collection compares things.
"""

import math

from .utils import BaseCommonGeometryObject


def _to_nurbs(shape):
    """Return `shape` with every face converted to a B-spline surface.

    The conversion is exact rather than a fit. A rational B-spline can represent a
    circle, and so a cylinder or a cone, with no error at all, which is what lets
    these models keep an analytic CSG counterpart.
    """
    import cadquery as cq
    from OCP.BRepBuilderAPI import BRepBuilderAPI_NurbsConvert

    return cq.Shape.cast(BRepBuilderAPI_NurbsConvert(shape.wrapped, True).Shape())


class NurbsCylinder(BaseCommonGeometryObject):
    """A cylinder whose curved face is a rational B-spline.

    The control case. It is the same shape as :class:`Cylinder`, so anything that
    differs between the two is down to the representation of the face and not to the
    geometry, which makes it the model to reach for when deciding whether a NURBS
    input is being handled worse than an analytic one.
    """

    def __init__(self, radius=5, height=10):
        if radius <= 0 or height <= 0:
            raise ValueError("radius and height must both be positive")
        self.radius = radius
        self.height = height

    def analytic_volumes(self):
        """Exact volume, pi r squared times the height.

        The conversion to B-splines is exact, so this is the volume of the
        analytic cylinder the faces came from."""
        return (
            math.pi * self.radius ** 2 * self.height,
        )

    def _csg_model(self, materials):
        import openmc

        cylinder = openmc.ZCylinder(r=self.radius, boundary_type="vacuum")
        z_top = openmc.ZPlane(z0=self.height / 2, boundary_type="vacuum")
        z_bot = openmc.ZPlane(z0=-self.height / 2, boundary_type="vacuum")

        region = -cylinder & +z_bot & -z_top

        cell = openmc.Cell(region=region, fill=materials[0])

        geometry = openmc.Geometry([cell])
        my_materials = openmc.Materials(materials)
        model = openmc.Model(geometry=geometry, materials=my_materials)
        return model

    def cadquery_assembly(self):
        import cadquery as cq

        assembly = cq.Assembly(name="nurbs_cylinder")
        cylinder = cq.Workplane("XY").cylinder(self.height, self.radius)
        assembly.add(_to_nurbs(cylinder.val()))
        return assembly


class NurbsTruncatedCone(BaseCommonGeometryObject):
    """A frustum lofted between two circles, with its faces left as B-splines.

    The lofted shape between two different cross-sections that #52 asked for. The
    loft itself is not the new part, since :class:`TruncatedCone` is built the same
    way; what is new is that the surface it produced is kept as a B-spline instead
    of being handed back as the cone OCCT recognises it to be.

    The two radii differ, so the B-spline is not the degenerate case of a constant
    cross-section and its control points move in both parameters.
    """

    def __init__(self, height=10, bottom_radius=5, top_radius=2):
        if bottom_radius <= top_radius:
            raise ValueError("bottom_radius should be greater than top_radius")
        if top_radius <= 0:
            raise ValueError("top_radius should be greater than 0")
        self.height = height
        self.bottom_radius = bottom_radius
        self.top_radius = top_radius

    def analytic_volumes(self):
        """Exact volume of the frustum.

        The conversion to B-splines is exact, so this is the volume of the
        analytic frustum the loft produced."""
        return (
            math.pi * self.height / 3
            * (self.bottom_radius ** 2
            + self.bottom_radius * self.top_radius
            + self.top_radius ** 2),
        )

    def _csg_model(self, materials):
        import openmc

        h = self.height
        r_bot = self.bottom_radius
        r_top = self.top_radius

        # Apex is above the frustum, where the two radii would converge to zero
        z_apex = 0.5 * h * (r_top + r_bot) / (r_bot - r_top)
        r2 = ((r_bot - r_top) / h) ** 2

        cone = openmc.ZCone(z0=z_apex, r2=r2)
        z_top = openmc.ZPlane(z0=0.5 * h, boundary_type="vacuum")
        z_bot = openmc.ZPlane(z0=-0.5 * h, boundary_type="vacuum")

        region = -cone & +z_bot & -z_top

        cell = openmc.Cell(region=region, fill=materials[0])

        geometry = openmc.Geometry([cell])
        my_materials = openmc.Materials(materials)
        model = openmc.Model(geometry=geometry, materials=my_materials)
        return model

    def cadquery_assembly(self):
        import cadquery as cq

        assembly = cq.Assembly(name="nurbs_truncated_cone")
        frustum = (
            cq.Workplane("XY")
            .transformed(offset=(0, 0, -0.5 * self.height))
            .circle(self.bottom_radius)
            .workplane(offset=self.height)
            .circle(self.top_radius)
            .loft()
        )
        assembly.add(_to_nurbs(frustum.val()))
        return assembly
