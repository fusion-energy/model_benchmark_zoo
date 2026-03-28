import math

from .utils import BaseCommonGeometryObject


class Pyramid(BaseCommonGeometryObject):
    def __init__(self, base_width=10, height=10):
        self.base_width = base_width
        self.height = height

    def csg_model(self, materials):
        import openmc

        w = self.base_width / 2
        h = self.height

        # Bounding box
        box = openmc.model.RectangularParallelepiped(
            -w, w, -w, w, -h / 2, h / 2, boundary_type="vacuum"
        )

        # Four inclined planes converging at apex (0, 0, h/2)
        # At height z the half-width is w * (h/2 - z) / h
        # +x face: h*x + w*z = w*h/2
        px = openmc.Plane(a=h, b=0, c=w, d=w * h / 2)
        # -x face: -h*x + w*z = w*h/2
        mx = openmc.Plane(a=-h, b=0, c=w, d=w * h / 2)
        # +y face: h*y + w*z = w*h/2
        py = openmc.Plane(a=0, b=h, c=w, d=w * h / 2)
        # -y face: -h*y + w*z = w*h/2
        my = openmc.Plane(a=0, b=-h, c=w, d=w * h / 2)

        region_material = -box & -px & -mx & -py & -my
        region_void = -box & (+px | +mx | +py | +my)

        cell1 = openmc.Cell(region=region_material, fill=materials[0])
        cell2 = openmc.Cell(region=region_void)

        geometry = openmc.Geometry([cell1, cell2])
        my_materials = openmc.Materials(materials)
        model = openmc.Model(geometry=geometry, materials=my_materials)
        return model

    def cadquery_assembly(self):
        import cadquery as cq

        w = self.base_width
        h = self.height

        taper = math.degrees(math.atan2(w, 2 * h))
        solid = (
            cq.Workplane("XY")
            .workplane(offset=-h / 2)
            .rect(w, w)
            .extrude(h, taper=taper)
        )

        assembly = cq.Assembly(name="pyramid")
        assembly.add(solid)
        return assembly
