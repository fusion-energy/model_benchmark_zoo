import math

from .utils import BaseCommonGeometryObject

class CylinderTangentToPlate(BaseCommonGeometryObject):
    """A cylinder resting on a flat plate, touching it along one line.

    The curved to planar version of tangency, and the one that most resembles a
    real assembly: a pin laid in a channel or a tube against a wall. Where
    :class:`TangentSpheres` share a single point, these two solids share a whole
    line, so a mesher gets the degenerate zero angle contact along a feature it has
    to discretise rather than at one vertex it could round off.

    The two sides of the contact discretise differently, which is the point. The
    plate's face is planar, so it is triangulated as coarsely as its boundary
    allows and its edge runs dead straight along the contact. The cylinder's face
    is curved, so it is refined by chord deflection and the facet nearest the plate
    lies inside the true surface. The contact therefore opens into a wedge shaped
    gap whose width is set by the cylinder's faceting alone.

    The radius is 4 rather than smaller because the volume a facetted cylinder
    loses grows as the square of the edge length over the radius, and a small
    radius would spend the tally comparison's tolerance on the discretisation
    instead of on the geometry.
    """

    def __init__(self, plate_width=12, plate_thickness=4,
                 cylinder_radius=4, cylinder_length=10):
        for name, value in (("plate_width", plate_width),
                            ("plate_thickness", plate_thickness),
                            ("cylinder_radius", cylinder_radius),
                            ("cylinder_length", cylinder_length)):
            if value <= 0:
                raise ValueError(f"{name} must be positive")
        if cylinder_length > plate_width:
            raise ValueError(
                "cylinder_length must not exceed plate_width, so that the contact "
                "line stays within the plate's face"
            )
        self.plate_width = plate_width
        self.plate_thickness = plate_thickness
        self.cylinder_radius = cylinder_radius
        self.cylinder_length = cylinder_length

    @property
    def axis_height(self):
        """Height of the cylinder's axis, set so it touches the plate's top face."""
        return self.plate_thickness / 2 + self.cylinder_radius

    def analytic_volumes(self):
        """Exact volume of the plate and of the cylinder resting on it."""
        return (
            self.plate_width ** 2 * self.plate_thickness,
            math.pi * self.cylinder_radius ** 2 * self.cylinder_length,
        )

    def _csg_model(self, materials):
        import openmc

        w = self.plate_width
        t = self.plate_thickness
        r = self.cylinder_radius
        length = self.cylinder_length

        plate = openmc.model.RectangularParallelepiped(
            -w / 2, w / 2, -w / 2, w / 2, -t / 2, t / 2,
            boundary_type="vacuum"
        )

        # Axis along y at the height that puts the surface on the plate's top face
        cylinder = openmc.YCylinder(x0=0.0, z0=self.axis_height, r=r,
                                    boundary_type="vacuum")
        y_front = openmc.YPlane(y0=-length / 2, boundary_type="vacuum")
        y_back = openmc.YPlane(y0=length / 2, boundary_type="vacuum")

        cell1 = openmc.Cell(region=-plate, fill=materials[0])
        cell2 = openmc.Cell(
            region=-cylinder & +y_front & -y_back, fill=materials[1]
        )

        geometry = openmc.Geometry([cell1, cell2])
        my_materials = openmc.Materials(materials)
        model = openmc.Model(geometry=geometry, materials=my_materials)
        return model

    def cadquery_assembly(self):
        import cadquery as cq

        # Solids are added in the same order as the materials in csg_model, as
        # cad_to_dagmc assigns material_tags[i] to the i-th solid of the assembly.
        assembly = cq.Assembly(name="cylinder_tangent_to_plate")

        assembly.add(
            cq.Workplane("XY").box(
                self.plate_width, self.plate_width, self.plate_thickness
            )
        )
        assembly.add(
            cq.Workplane("XY")
            .transformed(offset=(0, 0, self.axis_height))
            .cylinder(self.cylinder_length, self.cylinder_radius, direct=(0, 1, 0))
        )
        return assembly
