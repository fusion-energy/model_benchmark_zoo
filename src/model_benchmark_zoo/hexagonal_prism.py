import math

from .utils import BaseCommonGeometryObject


class HexagonalPrism(BaseCommonGeometryObject):
    def __init__(self, outer_radius=5, height=10):
        self.outer_radius = outer_radius
        self.height = height

    def csg_model(self, materials):
        import openmc

        r = self.outer_radius
        h = self.height

        hex_prism = openmc.model.HexagonalPrism(
            edge_length=r, orientation="x", boundary_type="vacuum"
        )
        z_top = openmc.ZPlane(z0=h / 2, boundary_type="vacuum")
        z_bot = openmc.ZPlane(z0=-h / 2, boundary_type="vacuum")

        region = -hex_prism & +z_bot & -z_top
        cell = openmc.Cell(region=region, fill=materials[0])

        geometry = openmc.Geometry([cell])
        my_materials = openmc.Materials(materials)
        model = openmc.Model(geometry=geometry, materials=my_materials)
        return model

    def cadquery_assembly(self):
        import cadquery as cq

        r = self.outer_radius
        h = self.height

        assembly = cq.Assembly(name="hexagonal_prism")
        hexagon = (
            cq.Workplane("XY")
            .workplane(offset=-h / 2)
            .polygon(6, r * 2)
            .extrude(h)
        )
        assembly.add(hexagon)
        return assembly
