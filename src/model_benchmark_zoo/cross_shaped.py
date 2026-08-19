from .utils import BaseCommonGeometryObject

class CrossShaped(BaseCommonGeometryObject):
    """A single plus-shaped prism, non-convex at four reflex edges.

    The most reflex arrangement that still extrudes from one profile, and the top of
    the range that runs :class:`LShaped` at one reflex edge, :class:`TShaped` at two
    and this at four. All three keep the same dimensions and the same 255 volume, so
    the count is the only thing that varies, which is what makes it a sweep rather
    than three more shapes.

    All four of these edges run parallel to the extrusion axis and none of them meet.
    :class:`BlanketModule`'s wall reaches twelve, but in three directions and meeting
    at eight vertices, so it varies more than the count on its own.

    :class:`CrossJunction` is not this. There the cross is three solids sharing
    faces, each of them convex, so no single boundary is reflex.
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
        """Exact volume, the two bars with the square they overlap counted once."""
        return (
            self.width * self.leg_thickness * self.height
            + self.length * self.leg_thickness * self.height
            - self.leg_thickness ** 2 * self.height,
        )

    def _csg_model(self, materials):
        import openmc

        l = self.length
        w = self.width
        t = self.leg_thickness
        h = self.height

        z_bot = openmc.ZPlane(z0=-h / 2, boundary_type="vacuum")
        z_top = openmc.ZPlane(z0=h / 2, boundary_type="vacuum")

        x_left = openmc.XPlane(x0=-w / 2, boundary_type="vacuum")
        x_right = openmc.XPlane(x0=w / 2, boundary_type="vacuum")
        y_bot = openmc.YPlane(y0=-l / 2, boundary_type="vacuum")
        y_top = openmc.YPlane(y0=l / 2, boundary_type="vacuum")

        x_arm_left = openmc.XPlane(x0=-t / 2)
        x_arm_right = openmc.XPlane(x0=t / 2)
        y_arm_bot = openmc.YPlane(y0=-t / 2)
        y_arm_top = openmc.YPlane(y0=t / 2)

        # The two bars overlap in the middle, so the union counts it once
        region_horizontal = (
            +x_left & -x_right & +y_arm_bot & -y_arm_top & +z_bot & -z_top
        )
        region_vertical = (
            +x_arm_left & -x_arm_right & +y_bot & -y_top & +z_bot & -z_top
        )

        cell = openmc.Cell(
            region=region_horizontal | region_vertical, fill=materials[0]
        )

        geometry = openmc.Geometry([cell])
        my_materials = openmc.Materials(materials)
        model = openmc.Model(geometry=geometry, materials=my_materials)
        return model

    def cadquery_assembly(self):
        import cadquery as cq

        assembly = cq.Assembly(name="cross_shaped")

        horizontal = cq.Workplane("XY").box(
            self.width, self.leg_thickness, self.height
        )
        vertical = cq.Workplane("XY").box(
            self.leg_thickness, self.length, self.height
        )

        assembly.add(horizontal.union(vertical))
        return assembly
