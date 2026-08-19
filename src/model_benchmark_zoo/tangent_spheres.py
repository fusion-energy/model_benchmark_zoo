import math

from .utils import BaseCommonGeometryObject

class TangentSpheres(BaseCommonGeometryObject):
    """Two spheres of different radii touching at a single point.

    Tangential contact is the limiting case of a small dihedral angle: where the
    two surfaces meet the angle between them is zero, and it stays zero along the
    whole of the contact. The zoo had no deliberate tangency anywhere.
    :class:`OverlappingSpheres` interpenetrates rather than touches, and
    :class:`CylinderInBox` has a radius 3 cylinder inside a width 12 box, so
    nothing in it comes near a face.

    Point contact is the hardest version of it, since the two solids share exactly
    one point of the whole of space. Neither faceting nor tetrahedralisation can
    reproduce that: a facet chord lies inside the surface it approximates, so the
    two faceted spheres pull apart into a near contact that the mesher has to
    resolve without collapsing an element into the gap.

    The radii differ so that the two surfaces have different curvature where they
    meet, which stops a mesher getting the contact right for the wrong reason by
    placing the same facet pattern on both sides of it. Neither is made smaller
    than 4, because the volume a facetted sphere loses grows as the square of the
    edge length over the radius, and at radius 3 that alone is 1.5 percent of the
    smaller sphere at the edge lengths the tests ask for, which is most of the
    tolerance the tally comparison allows.
    """

    def __init__(self, first_radius=5, second_radius=4):
        if first_radius <= 0 or second_radius <= 0:
            raise ValueError("both radii must be positive")
        self.first_radius = first_radius
        self.second_radius = second_radius

    def analytic_volumes(self):
        """Exact volume of each sphere."""
        return (
            4 / 3 * math.pi * self.first_radius ** 3,
            4 / 3 * math.pi * self.second_radius ** 3,
        )

    def _csg_model(self, materials):
        import openmc

        r1 = self.first_radius
        r2 = self.second_radius

        # Centres are placed either side of the origin at their own radius, so the
        # two surfaces meet there exactly and nowhere else.
        first = openmc.Sphere(x0=-r1, r=r1, boundary_type="vacuum")
        second = openmc.Sphere(x0=r2, r=r2, boundary_type="vacuum")

        cell1 = openmc.Cell(region=-first, fill=materials[0])
        cell2 = openmc.Cell(region=-second, fill=materials[1])

        geometry = openmc.Geometry([cell1, cell2])
        my_materials = openmc.Materials(materials)
        model = openmc.Model(geometry=geometry, materials=my_materials)
        return model

    def cadquery_assembly(self):
        import cadquery as cq

        r1 = self.first_radius
        r2 = self.second_radius

        # Solids are added in the same order as the materials in csg_model, as
        # cad_to_dagmc assigns material_tags[i] to the i-th solid of the assembly.
        assembly = cq.Assembly(name="tangent_spheres")
        assembly.add(cq.Workplane("XY").transformed(offset=(-r1, 0, 0)).sphere(r1))
        assembly.add(cq.Workplane("XY").transformed(offset=(r2, 0, 0)).sphere(r2))
        return assembly
