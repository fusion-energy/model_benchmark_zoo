from .utils import BaseCommonGeometryObject

class TShaped(BaseCommonGeometryObject):
    """A single T-shaped prism, non-convex at two reflex edges.

    A mesher filling a solid up to a boundary it is not allowed to move has to
    recover the reflex edges rather than mesh a convex hull, and the zoo gave that
    path only two cases to work with, at opposite extremes. :class:`LShaped` has one
    reflex edge and :class:`BlanketModule`'s wall has twelve, which is a step too
    large to tell whether the cost of recovering an edge grows with how many there
    are or whether L simply happens to be easy.

    This fills the step in at two, keeping every dimension of :class:`LShaped` so
    the count of reflex edges is the only thing that changes.

    :class:`TJunction` is not this. There the T is built from two solids that share
    a face, and each solid on its own is convex, so no single boundary is reflex.
    """

    def __init__(self, length=10, width=10, leg_thickness=3, height=5):
        if leg_thickness >= length or leg_thickness >= width:
            raise ValueError("leg_thickness must be less than both length and width")
        if height <= 0:
            raise ValueError("height must be positive")
        self.length = length
        self.width = width
        self.leg_thickness = leg_thickness
        self.height = height

    def analytic_volumes(self):
        """Exact volume, the bar plus the stem that meets it."""
        return (
            self.width * self.leg_thickness * self.height
            + self.leg_thickness * (self.length - self.leg_thickness)
            * self.height,
        )

    def _csg_model(self, materials):
        import openmc

        l = self.length
        w = self.width
        t = self.leg_thickness
        h = self.height

        z_bot = openmc.ZPlane(z0=-h / 2, boundary_type="vacuum")
        z_top = openmc.ZPlane(z0=h / 2, boundary_type="vacuum")

        # Cross bar: the full width, thickness t, along the -y edge
        x_left = openmc.XPlane(x0=-w / 2, boundary_type="vacuum")
        x_right = openmc.XPlane(x0=w / 2, boundary_type="vacuum")
        y_bot = openmc.YPlane(y0=-l / 2, boundary_type="vacuum")
        y_bar_top = openmc.YPlane(y0=-l / 2 + t)

        # Stem: thickness t, centred in x, reaching the +y edge
        x_stem_left = openmc.XPlane(x0=-t / 2)
        x_stem_right = openmc.XPlane(x0=t / 2)
        y_top = openmc.YPlane(y0=l / 2, boundary_type="vacuum")

        region_bar = +x_left & -x_right & +y_bot & -y_bar_top & +z_bot & -z_top
        region_stem = (
            +x_stem_left & -x_stem_right & +y_bar_top & -y_top & +z_bot & -z_top
        )

        cell = openmc.Cell(region=region_bar | region_stem, fill=materials[0])

        geometry = openmc.Geometry([cell])
        my_materials = openmc.Materials(materials)
        model = openmc.Model(geometry=geometry, materials=my_materials)
        return model

    def cadquery_assembly(self):
        import cadquery as cq

        l = self.length
        w = self.width
        t = self.leg_thickness
        h = self.height

        assembly = cq.Assembly(name="t_shaped")

        bar = cq.Workplane("XY").transformed(
            offset=(0, -l / 2 + t / 2, 0)
        ).box(w, t, h)
        stem = cq.Workplane("XY").transformed(
            offset=(0, (-l / 2 + t + l / 2) / 2, 0)
        ).box(t, l - t, h)

        assembly.add(bar.union(stem))
        return assembly
