from .utils import BaseCommonGeometryObject

class LargePlanarFace(BaseCommonGeometryObject):
    """A square plate whose flat faces span many times the target edge length.

    BRepMesh sizes triangles by chord deflection, and a planar face has no
    curvature to deflect from, so it is triangulated as coarsely as its boundary
    allows however fine an edge length is asked for. A square face arrives as two
    triangles whatever ``span`` is, which means the longest edge of the surface
    mesh grows with the plate while the requested edge length stays put.

    ``span`` is the variable to sweep. The zoo covers the small end of it already,
    with :class:`Cuboid` and :class:`ThinPlate` both 10 units across, so the
    default here is deliberately large: at the 0.5 unit edge length the tests ask
    for, a 50 unit face is 100 target edge lengths wide and its diagonal is 141.
    """

    def __init__(self, span=50, thickness=5):
        if span <= 0 or thickness <= 0:
            raise ValueError("span and thickness must both be positive")
        self.span = span
        self.thickness = thickness

    def analytic_volumes(self):
        """Exact volume, the square face times the thickness."""
        return (
            self.span ** 2 * self.thickness,
        )

    def _csg_model(self, materials):
        import openmc

        surface = openmc.model.RectangularParallelepiped(
            -self.span / 2, self.span / 2,
            -self.span / 2, self.span / 2,
            -self.thickness / 2, self.thickness / 2,
            boundary_type="vacuum"
        )
        region = -surface
        cell = openmc.Cell(region=region, fill=materials[0])
        geometry = openmc.Geometry([cell])
        my_materials = openmc.Materials(materials)
        model = openmc.Model(geometry=geometry, materials=my_materials)
        return model

    def cadquery_assembly(self):
        import cadquery as cq

        assembly = cq.Assembly(name="large_planar_face")
        plate = cq.Workplane("XY").box(self.span, self.span, self.thickness)
        assembly.add(plate)
        return assembly
