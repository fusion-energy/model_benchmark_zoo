from .utils import BaseCommonGeometryObject

class FuelPinCell(BaseCommonGeometryObject):
    def __init__(self, fuel_radius=2, clad_outer_radius=2.5, pitch=8, height=10):
        self.fuel_radius = fuel_radius
        self.clad_outer_radius = clad_outer_radius
        self.pitch = pitch
        self.height = height

    def csg_model(self, materials):
        import openmc

        rf = self.fuel_radius
        rc = self.clad_outer_radius
        p = self.pitch
        h = self.height

        fuel_cyl = openmc.ZCylinder(r=rf)
        clad_cyl = openmc.ZCylinder(r=rc)
        box = openmc.model.RectangularParallelepiped(
            -p / 2, p / 2, -p / 2, p / 2, -h / 2, h / 2,
            boundary_type="vacuum"
        )

        region_fuel = -fuel_cyl & -box
        region_clad = +fuel_cyl & -clad_cyl & -box
        region_coolant = +clad_cyl & -box

        cell1 = openmc.Cell(region=region_fuel, fill=materials[0])
        cell2 = openmc.Cell(region=region_clad, fill=materials[1])
        cell3 = openmc.Cell(region=region_coolant, fill=materials[2])

        geometry = openmc.Geometry([cell1, cell2, cell3])
        my_materials = openmc.Materials(materials)
        model = openmc.Model(geometry=geometry, materials=my_materials)
        return model

    def cadquery_assembly(self):
        import cadquery as cq

        rf = self.fuel_radius
        rc = self.clad_outer_radius
        p = self.pitch
        h = self.height

        assembly = cq.Assembly(name="fuel_pin_cell")
        fuel = cq.Workplane("XY").cylinder(h, rf)
        assembly.add(fuel)

        clad = cq.Workplane("XY").cylinder(h, rc).cut(cq.Workplane("XY").cylinder(h, rf))
        assembly.add(clad)

        box = cq.Workplane("XY").box(p, p, h)
        coolant = box.cut(cq.Workplane("XY").cylinder(h, rc))
        assembly.add(coolant)

        return assembly
