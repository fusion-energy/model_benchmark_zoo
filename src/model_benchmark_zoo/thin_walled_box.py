from .utils import BaseCommonGeometryObject

class ThinWalledBox(BaseCommonGeometryObject):
    """A hollow box, thin walled and entirely planar.

    The zoo's thin features were curved, or open, or not free to be swept.
    :class:`ThinWalledSphere` and :class:`ThinWalledCylinder` are shells, but their
    walls are curved, so a mesher sizing triangles by chord deflection refines them
    for their curvature and gets the wall resolved through its thickness as a side
    effect of that. :class:`ThinPlate` and :class:`ThinGap` are planar but neither
    encloses anything, so their thin dimension is bounded by faces that reach the
    outside. :class:`BlanketModule`'s wall is a planar shell that does enclose, but
    it reaches only 13 to 1 at its widest and its thickness cannot be moved without
    also moving the breeder and the coolant channel inside it.

    A planar shell gets none of that help. Its walls carry no curvature to be refined
    by, so they arrive at whatever the boundary alone dictates, and each wall spans
    the full width of the box while being a fraction of it thick. At the default sizes
    that is 50 to 1, with a wall 0.2 units thick against a face 10 units across, and
    ``wall_thickness`` is the only thing that has to move to sweep it.

    The wall thickness matches :class:`ThinWalledCylinder` exactly, so the two can be
    compared directly at the same wall for a curved and a planar shell.

    The cavity is fully enclosed, as in :class:`BoxWithSphericalCavity`, so it ends up
    part of the surrounding void that :meth:`csg_model` builds rather than a region
    the model declares.
    """

    def __init__(self, width=10, wall_thickness=0.2):
        if wall_thickness <= 0:
            raise ValueError("wall_thickness must be positive")
        if wall_thickness >= width / 2:
            raise ValueError(
                "wall_thickness must be less than half the width, so that the box "
                "is hollow rather than solid"
            )
        self.width = width
        self.wall_thickness = wall_thickness

    @property
    def inner_width(self):
        return self.width - 2 * self.wall_thickness

    @property
    def span_to_thickness(self):
        """How many wall thicknesses across the box is, the variable to sweep."""
        return self.width / self.wall_thickness

    def analytic_volumes(self):
        """Exact volume of the shell, the outer cube less the cavity."""
        return (
            self.width ** 3 - self.inner_width ** 3,
        )

    def _csg_model(self, materials):
        import openmc

        half = self.width / 2
        inner_half = self.inner_width / 2

        outer = openmc.model.RectangularParallelepiped(
            -half, half, -half, half, -half, half,
            boundary_type="vacuum"
        )
        inner = openmc.model.RectangularParallelepiped(
            -inner_half, inner_half, -inner_half, inner_half,
            -inner_half, inner_half,
        )

        region = -outer & ~(-inner)

        cell = openmc.Cell(region=region, fill=materials[0])

        geometry = openmc.Geometry([cell])
        my_materials = openmc.Materials(materials)
        model = openmc.Model(geometry=geometry, materials=my_materials)
        return model

    def cadquery_assembly(self):
        import cadquery as cq

        assembly = cq.Assembly(name="thin_walled_box")

        outer = cq.Workplane("XY").box(self.width, self.width, self.width)
        inner = cq.Workplane("XY").box(
            self.inner_width, self.inner_width, self.inner_width
        )
        assembly.add(outer.cut(inner))
        return assembly
