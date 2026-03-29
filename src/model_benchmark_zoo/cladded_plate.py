from .utils import BaseCommonGeometryObject

class CladdedPlate(BaseCommonGeometryObject):
    def __init__(self, width=20, length=20, core_thickness=4, clad_thickness=1):
        self.width = width
        self.length = length
        self.core_thickness = core_thickness
        self.clad_thickness = clad_thickness

    def csg_model(self, materials):
        import openmc

        w = self.width
        l = self.length
        tc = self.core_thickness
        t_clad = self.clad_thickness
        total = tc + 2 * t_clad

        x_min = openmc.XPlane(x0=-w / 2, boundary_type="vacuum")
        x_max = openmc.XPlane(x0=w / 2, boundary_type="vacuum")
        y_min = openmc.YPlane(y0=-l / 2, boundary_type="vacuum")
        y_max = openmc.YPlane(y0=l / 2, boundary_type="vacuum")
        z_bot = openmc.ZPlane(z0=-total / 2, boundary_type="vacuum")
        z_core_bot = openmc.ZPlane(z0=-tc / 2)
        z_core_top = openmc.ZPlane(z0=tc / 2)
        z_top = openmc.ZPlane(z0=total / 2, boundary_type="vacuum")

        xy_region = +x_min & -x_max & +y_min & -y_max

        region_bot_clad = xy_region & +z_bot & -z_core_bot
        region_core = xy_region & +z_core_bot & -z_core_top
        region_top_clad = xy_region & +z_core_top & -z_top

        cell1 = openmc.Cell(region=region_bot_clad, fill=materials[0])
        cell2 = openmc.Cell(region=region_core, fill=materials[1])
        cell3 = openmc.Cell(region=region_top_clad, fill=materials[2])

        geometry = openmc.Geometry([cell1, cell2, cell3])
        my_materials = openmc.Materials(materials)
        model = openmc.Model(geometry=geometry, materials=my_materials)
        return model

    def cadquery_assembly(self):
        import cadquery as cq

        w = self.width
        l = self.length
        tc = self.core_thickness
        t_clad = self.clad_thickness

        assembly = cq.Assembly(name="cladded_plate")

        bot_clad = cq.Workplane("XY").transformed(offset=(0, 0, -(tc + t_clad) / 2)).box(w, l, t_clad)
        assembly.add(bot_clad)

        core = cq.Workplane("XY").box(w, l, tc)
        assembly.add(core)

        top_clad = cq.Workplane("XY").transformed(offset=(0, 0, (tc + t_clad) / 2)).box(w, l, t_clad)
        assembly.add(top_clad)

        return assembly
