from .utils import BaseCommonGeometryObject

class HexagonalLatticeCell(BaseCommonGeometryObject):
    def __init__(self, hex_edge_length=5, pin_radius=1.5, height=10):
        self.hex_edge_length = hex_edge_length
        self.pin_radius = pin_radius
        self.height = height

    def csg_model(self, materials):
        import openmc

        r_pin = self.pin_radius
        edge = self.hex_edge_length
        h = self.height

        hex_prism = openmc.model.HexagonalPrism(edge_length=edge, orientation="x", boundary_type="vacuum")
        z_top = openmc.ZPlane(z0=h / 2, boundary_type="vacuum")
        z_bot = openmc.ZPlane(z0=-h / 2, boundary_type="vacuum")
        pin = openmc.ZCylinder(r=r_pin)

        region_pin = -pin & +z_bot & -z_top
        region_moderator = -hex_prism & +z_bot & -z_top & +pin

        cell1 = openmc.Cell(region=region_pin, fill=materials[0])
        cell2 = openmc.Cell(region=region_moderator, fill=materials[1])

        geometry = openmc.Geometry([cell1, cell2])
        my_materials = openmc.Materials(materials)
        model = openmc.Model(geometry=geometry, materials=my_materials)
        return model

    def cadquery_assembly(self):
        import cadquery as cq

        edge = self.hex_edge_length
        h = self.height
        r_pin = self.pin_radius

        assembly = cq.Assembly(name="hexagonal_lattice_cell")
        pin = cq.Workplane("XY").cylinder(h, r_pin)
        assembly.add(pin)

        hex_prism = cq.Workplane("XY").workplane(offset=-h / 2).polygon(6, edge * 2).extrude(h)
        hex_shell = hex_prism.cut(cq.Workplane("XY").cylinder(h, r_pin))
        assembly.add(hex_shell)

        return assembly
