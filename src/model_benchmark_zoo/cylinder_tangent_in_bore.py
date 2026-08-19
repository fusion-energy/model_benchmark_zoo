import math

from .utils import BaseCommonGeometryObject

class CylinderTangentInBore(BaseCommonGeometryObject):
    """A rod inside a pipe, touching the bore along one line from the inside.

    Internal tangency, which is the case the other two tangency models do not
    reach. :class:`TangentSpheres` and :class:`CylinderTangentToPlate` both touch
    from outside, so the solid the mesher is filling is locally convex on both
    sides of the contact and the void between them opens out. Here the bore curves
    the same way as the rod, so the void closes in on the contact from both sides
    and forms a cusp: two surfaces almost parallel over a region far wider than the
    gap between them.

    That is the shape a mesher handles worst, because the region needing small
    elements is not confined to the contact but spreads out along the whole cusp.
    Which way the cusp errs depends on the mesher, since facets on the rod fall
    inside it while facets on the bore fall inside the pipe, that is outwards, so
    the two can either part or overlap depending on where the vertices land.

    The radii are kept above 2 because the volume a facetted cylinder loses grows
    as the square of the edge length over the radius, and a thin rod would spend
    the tally comparison's tolerance on discretisation rather than geometry.
    """

    def __init__(self, inner_radius=6, outer_radius=8, height=10, rod_radius=2.5):
        if not 0 < inner_radius < outer_radius:
            raise ValueError("radii must satisfy 0 < inner_radius < outer_radius")
        if not 0 < rod_radius < inner_radius:
            raise ValueError(
                "rod_radius must be positive and smaller than inner_radius, so the "
                "rod fits inside the bore"
            )
        if height <= 0:
            raise ValueError("height must be positive")
        self.inner_radius = inner_radius
        self.outer_radius = outer_radius
        self.height = height
        self.rod_radius = rod_radius

    @property
    def rod_offset(self):
        """Distance the rod's axis sits from the bore's, to make the two touch."""
        return self.inner_radius - self.rod_radius

    def analytic_volumes(self):
        """Exact volume of the pipe wall and of the rod inside the bore."""
        return (
            math.pi * (self.outer_radius ** 2 - self.inner_radius ** 2)
            * self.height,
            math.pi * self.rod_radius ** 2 * self.height,
        )

    def _csg_model(self, materials):
        import openmc

        h = self.height

        bore = openmc.ZCylinder(r=self.inner_radius)
        outer = openmc.ZCylinder(r=self.outer_radius, boundary_type="vacuum")
        z_bot = openmc.ZPlane(z0=-h / 2, boundary_type="vacuum")
        z_top = openmc.ZPlane(z0=h / 2, boundary_type="vacuum")

        # Offset so the rod's surface meets the bore from the inside
        rod = openmc.ZCylinder(x0=self.rod_offset, r=self.rod_radius,
                               boundary_type="vacuum")

        cell1 = openmc.Cell(
            region=+bore & -outer & +z_bot & -z_top, fill=materials[0]
        )
        cell2 = openmc.Cell(region=-rod & +z_bot & -z_top, fill=materials[1])

        geometry = openmc.Geometry([cell1, cell2])
        my_materials = openmc.Materials(materials)
        model = openmc.Model(geometry=geometry, materials=my_materials)
        return model

    def cadquery_assembly(self):
        import cadquery as cq

        h = self.height

        # Solids are added in the same order as the materials in csg_model, as
        # cad_to_dagmc assigns material_tags[i] to the i-th solid of the assembly.
        assembly = cq.Assembly(name="cylinder_tangent_in_bore")

        pipe = cq.Workplane("XY").cylinder(h, self.outer_radius).cut(
            cq.Workplane("XY").cylinder(h + 2, self.inner_radius)
        )
        assembly.add(pipe)
        assembly.add(
            cq.Workplane("XY")
            .transformed(offset=(self.rod_offset, 0, 0))
            .cylinder(h, self.rod_radius)
        )
        return assembly
