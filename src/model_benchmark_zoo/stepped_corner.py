from .utils import BaseCommonGeometryObject

class SteppedCorner(BaseCommonGeometryObject):
    """A box with a rectangular block removed from one corner.

    At the default sizes this is a cube with one octant taken out, the corner the
    finite element literature calls the Fichera corner. Three reflex edges meet at
    one reflex vertex, and that is the whole of the solid's non-convexity.

    A reflex vertex is not new to the zoo, but an isolated one is. Counting the
    reflex edges of every all-planar solid, by how much of a small circle drawn
    across each edge is material:

        solid                   reflex edges   directions   reflex vertices
        LShaped                            1            1                 0
        SteppedCorner                      3            3                 1
        NotchedBox                         8            3                 4
        BlanketModule wall                12            3                 8

    The last two put a mesher's difficulty in several places at once. This has
    exactly one, which is the fewest a reflex vertex can be studied with, and it is
    the point a conforming mesher has least freedom around, since every element
    touching it is squeezed between three faces it may not move.

    :class:`SteppedCylinder` is the curved counterpart of this shape but is built
    from two solids, so its step is an interface between volumes rather than a
    reflex feature of one boundary.
    """

    def __init__(self, width=10, corner_width=5):
        if not 0 < corner_width < width:
            raise ValueError("corner_width must satisfy 0 < corner_width < width")
        self.width = width
        self.corner_width = corner_width

    @property
    def cut_position(self):
        """Coordinate of the three planes that bound the removed block inside."""
        return self.width / 2 - self.corner_width

    def analytic_volumes(self):
        """Exact volume, the cube less the corner block removed from it."""
        return (
            self.width ** 3 - self.corner_width ** 3,
        )

    def _csg_model(self, materials):
        import openmc

        w = self.width

        box = openmc.model.RectangularParallelepiped(
            -w / 2, w / 2, -w / 2, w / 2, -w / 2, w / 2,
            boundary_type="vacuum"
        )

        # The removed block is bounded outwardly by the faces of the box itself, so
        # only the three inward planes are needed and no surface is duplicated.
        cut = self.cut_position
        x_cut = openmc.XPlane(x0=cut)
        y_cut = openmc.YPlane(y0=cut)
        z_cut = openmc.ZPlane(z0=cut)

        region = -box & ~(+x_cut & +y_cut & +z_cut)

        cell = openmc.Cell(region=region, fill=materials[0])

        geometry = openmc.Geometry([cell])
        my_materials = openmc.Materials(materials)
        model = openmc.Model(geometry=geometry, materials=my_materials)
        return model

    def cadquery_assembly(self):
        import cadquery as cq

        w = self.width
        cut = self.cut_position

        assembly = cq.Assembly(name="stepped_corner")

        box = cq.Workplane("XY").box(w, w, w)
        # The tool starts on the three inward planes and overshoots the box on the
        # other three sides, so the cut never has to resolve coincident faces.
        side = self.corner_width + w
        corner = cq.Workplane("XY").transformed(
            offset=(cut + side / 2, cut + side / 2, cut + side / 2)
        ).box(side, side, side)

        assembly.add(box.cut(corner))
        return assembly
