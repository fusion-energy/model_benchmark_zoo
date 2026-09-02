import math

from .utils import BaseCommonGeometryObject

class PartiallyEmbeddedSphere(BaseCommonGeometryObject):
    """A sphere resting in a spherical dimple on one flat face of a box.

    The sphere is only partly inside the box, so the surface the two solids share
    is a spherical cap and the boundary of that cap is a circle lying exactly in
    the plane of the box face. :class:`SphereInBox` already covers a curved solid
    enclosed by a rectilinear one, but there the sphere is entirely interior and
    the shared surface closes on itself without ever meeting a planar face.

    That circle is the point of the model. A curved interface running into a flat
    face puts the seam of two solids into the middle of a planar region, so the
    face has to be triangulated around a curve it does not itself contain, and
    both solids have to agree on every vertex along it. Meshers that handle a
    curved interface and a planar face separately can still get this wrong where
    the two meet, and a tetrahedral mesher working in that plane has to resolve
    the seam without the curvature cues it would get on the cap itself.

    The dimple is also a concave feature on an otherwise flat face, which is the
    opposite sense to :class:`BoxWithSphericalCavity` (fully enclosed) and to
    :class:`OverlappingSpheres` (curved meeting curved).

    ``penetration_depth`` is the variable to sweep. Driving it towards zero makes
    the cap shallower and the seam circle smaller, until the two solids touch over
    a region that faceting can barely represent; driving it towards
    ``sphere_radius`` makes the cap approach a hemisphere.
    """

    def __init__(self, box_width=30, sphere_radius=10, penetration_depth=5):
        if sphere_radius <= 0:
            raise ValueError("sphere_radius must be positive")
        if not 0 < penetration_depth < sphere_radius:
            raise ValueError(
                "penetration_depth must be between zero and sphere_radius, so "
                "that the sphere centre stays outside the box and the shared "
                "surface is a single spherical cap"
            )
        seam_radius = math.sqrt(
            2 * sphere_radius * penetration_depth - penetration_depth ** 2
        )
        if seam_radius >= box_width / 2:
            raise ValueError(
                "the dimple reaches the edge of the box face; reduce "
                "sphere_radius or penetration_depth, or widen the box"
            )

        self.box_width = box_width
        self.sphere_radius = sphere_radius
        self.penetration_depth = penetration_depth

    @property
    def sphere_centre_x(self):
        """Centre of the sphere, on the +x side of the box face at ``+width/2``."""
        return self.box_width / 2 - self.penetration_depth + self.sphere_radius

    @property
    def seam_radius(self):
        """Radius of the circle where the cap meets the flat face of the box."""
        return math.sqrt(
            2 * self.sphere_radius * self.penetration_depth
            - self.penetration_depth ** 2
        )

    def _cap_volume(self):
        """Volume of the spherical cap that is inside the box."""
        h = self.penetration_depth
        return math.pi * h ** 2 * (3 * self.sphere_radius - h) / 3

    def analytic_volumes(self):
        """Exact volume of the dimpled box and of the whole sphere.

        The box loses exactly the spherical cap that pokes into it. The sphere is
        a whole sphere: the part outside the box is still part of that solid, and
        the void around the model is what the transport sees beyond it.
        """
        return (
            self.box_width ** 3 - self._cap_volume(),
            4 / 3 * math.pi * self.sphere_radius ** 3,
        )

    def _csg_model(self, materials):
        import openmc

        w = self.box_width

        box_surface = openmc.model.RectangularParallelepiped(
            -w / 2, w / 2, -w / 2, w / 2, -w / 2, w / 2,
            boundary_type="vacuum"
        )
        sphere_surface = openmc.Sphere(
            x0=self.sphere_centre_x, r=self.sphere_radius
        )

        region_box = -box_surface & +sphere_surface
        region_sphere = -sphere_surface

        cell_box = openmc.Cell(region=region_box, fill=materials[0])
        cell_sphere = openmc.Cell(region=region_sphere, fill=materials[1])

        geometry = openmc.Geometry([cell_box, cell_sphere])
        my_materials = openmc.Materials(materials)
        model = openmc.Model(geometry=geometry, materials=my_materials)
        return model

    def cadquery_assembly(self):
        import cadquery as cq

        assembly = cq.Assembly(name="partially_embedded_sphere")

        box = cq.Workplane("XY").box(
            self.box_width, self.box_width, self.box_width
        )
        sphere = (
            cq.Workplane("XY").moveTo(self.sphere_centre_x, 0).sphere(
                self.sphere_radius
            )
        )

        assembly.add(box.cut(sphere))
        assembly.add(sphere)
        return assembly
