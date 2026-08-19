from .utils import BaseCommonGeometryObject

class NotchedBox(BaseCommonGeometryObject):
    """A box with a rectangular pocket cut into one face.

    Reflex edges came in only two arrangements before this. :class:`LShaped` is a
    prism, so its one reflex edge runs parallel to the extrusion axis and meets
    nothing. :class:`BlanketModule`'s wall is a closed shell, which puts twelve of
    them in three directions around a cavity with no opening at all. A pocket sits
    between the two: the cavity is open, so it is part of the one boundary a mesher
    has to fill up to, and it still carries reflex edges in three directions.

    Where those edges are is worth stating, because the rim is not one of them. At
    the rim, where the pocket meets the face it opens onto, the material fills a
    quarter of a small circle drawn across the edge, the same as any outer edge of
    a plain box, so it is convex. The eight reflex edges are the four upright ones
    where two pocket walls meet and the four around the pocket floor, and they meet
    three at a time at the floor's four corners, each of which has material in
    seven of its eight octants.

    The opening is also strictly interior to the face it is cut from, so that face
    keeps its outer boundary and gains a second loop. That is the island case that
    separates OCCT's gluing options on curved faces, here on a planar one.

    Unlike :class:`BoxWithSphericalCavity`, whose sphere is enclosed and leaves the
    outer boundary convex, this pocket is open to the outside and so is part of the
    one boundary a mesher has to fill up to.
    """

    def __init__(self, width=10, depth=10, height=10,
                 notch_width=4, notch_depth=4, notch_height=4):
        if notch_width >= width or notch_depth >= depth:
            raise ValueError(
                "the notch must be narrower than the box in both directions, so "
                "that its opening stays interior to the face"
            )
        if notch_height >= height:
            raise ValueError("notch_height must be less than height")
        self.width = width
        self.depth = depth
        self.height = height
        self.notch_width = notch_width
        self.notch_depth = notch_depth
        self.notch_height = notch_height

    def analytic_volumes(self):
        """Exact volume, the box less the pocket cut out of it."""
        return (
            self.width * self.depth * self.height
            - self.notch_width * self.notch_depth * self.notch_height,
        )

    def _csg_model(self, materials):
        import openmc

        w = self.width
        d = self.depth
        h = self.height

        box = openmc.model.RectangularParallelepiped(
            -w / 2, w / 2, -d / 2, d / 2, -h / 2, h / 2,
            boundary_type="vacuum"
        )

        # The notch reaches above the top of the box rather than stopping level
        # with it, so the two do not share a coincident plane. The intersection
        # with the box is what trims it back to the face.
        notch = openmc.model.RectangularParallelepiped(
            -self.notch_width / 2, self.notch_width / 2,
            -self.notch_depth / 2, self.notch_depth / 2,
            h / 2 - self.notch_height, h / 2 + 1,
        )

        region = -box & ~(-notch)

        cell = openmc.Cell(region=region, fill=materials[0])

        geometry = openmc.Geometry([cell])
        my_materials = openmc.Materials(materials)
        model = openmc.Model(geometry=geometry, materials=my_materials)
        return model

    def cadquery_assembly(self):
        import cadquery as cq

        h = self.height
        nh = self.notch_height

        assembly = cq.Assembly(name="notched_box")

        box = cq.Workplane("XY").box(self.width, self.depth, h)
        # As in the CSG model the cutting tool overshoots the top face, so the cut
        # is not asked to resolve two coincident planes.
        notch = cq.Workplane("XY").transformed(
            offset=(0, 0, h / 2 - nh + (nh + 1) / 2)
        ).box(self.notch_width, self.notch_depth, nh + 1)

        assembly.add(box.cut(notch))
        return assembly
