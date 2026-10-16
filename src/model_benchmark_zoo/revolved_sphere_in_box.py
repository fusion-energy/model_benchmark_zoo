import math

from .utils import BaseCommonGeometryObject


class RevolvedSphereInBox(BaseCommonGeometryObject):
    """A sphere made by revolving a semicircle, filling a spherical cavity in a box.

    The geometry is exactly :class:`SphereInBox`. The difference is in how the
    two solids are built. The cavity in the box is cut with ``sphere()``, which
    puts the poles of the spherical face on the z axis. The sphere that fills
    it is made the way it often is in a sketch based CAD tool, by revolving a
    semicircle about its diameter, here lying along the x axis. The two
    spherical faces are the same surface but their poles are a quarter turn
    apart, and no rotation is applied to either solid to get there.

    This is the situation that arises whenever a part and the cavity it sits in
    are modelled separately, which is the usual case for pebbles, pellets or
    balls placed in a matrix. :class:`SphereInBox` cuts the cavity with the
    same sphere it then places in it, so its two faces line up by construction
    and cannot exercise it.

    When OCCT imprints the two solids it keeps one copy of the shared spherical
    face, and the seam and pole edges of the other are left lying on it as
    internal edges that no other face uses. A mesher that triangulates the
    shared face then has to respect an open wire running across the middle of
    the surface, which is not something a single closed sphere ever asks of it.
    Faceting the shared face badly shows up directly as a wrong volume for the
    sphere and a matching error in the box.

    Args:
        box_width: edge length of the cubic box.
        sphere_radius: radius of the sphere and of the cavity it fills.
    """

    def __init__(self, box_width=12, sphere_radius=4):
        if sphere_radius >= box_width / 2:
            raise ValueError("sphere_radius should be less than half the box_width")
        self.box_width = box_width
        self.sphere_radius = sphere_radius

    def analytic_volumes(self):
        """Exact volume of the sphere and of the box around it."""
        return (
            4 / 3 * math.pi * self.sphere_radius ** 3,
            self.box_width ** 3 - 4 / 3 * math.pi * self.sphere_radius ** 3,
        )

    def _csg_model(self, materials):
        import openmc

        w = self.box_width
        r = self.sphere_radius

        box = openmc.model.RectangularParallelepiped(
            -w / 2, w / 2, -w / 2, w / 2, -w / 2, w / 2,
            boundary_type="vacuum"
        )
        sphere = openmc.Sphere(r=r)

        region_sphere = -sphere
        region_box = -box & +sphere

        cell_sphere = openmc.Cell(region=region_sphere, fill=materials[0])
        cell_box = openmc.Cell(region=region_box, fill=materials[1])

        geometry = openmc.Geometry([cell_sphere, cell_box])
        my_materials = openmc.Materials(materials)
        model = openmc.Model(geometry=geometry, materials=my_materials)
        return model

    def cadquery_assembly(self):
        import cadquery as cq

        w = self.box_width
        r = self.sphere_radius

        assembly = cq.Assembly(name="revolved_sphere_in_box")

        # Semicircle in the xy plane closed along the x axis, revolved about
        # that axis, so the poles of this sphere are at x = -r and x = r.
        sphere = (
            cq.Workplane("XY")
            .moveTo(-r, 0)
            .threePointArc((0, r), (r, 0))
            .close()
            .revolve(360, (-r, 0, 0), (r, 0, 0))
        )
        # The cavity is cut with sphere(), whose poles are at z = -r and z = r.
        box_shell = cq.Workplane("XY").box(w, w, w).cut(cq.Workplane().sphere(r))

        assembly.add(sphere)
        assembly.add(box_shell)
        return assembly
