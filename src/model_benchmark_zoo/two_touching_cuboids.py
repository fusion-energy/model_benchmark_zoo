import cadquery as cq
import openmc
from cad_to_dagmc import CadToDagmc

#     *----------*----*
#     |          |    |
#     |          |    |
#     |          |    |
#     *----------*----*

class Cuboid:
    def __init__(self, materials, width1=10, width2=4):
        self.width1 = width1
        self.width2 = width2
        self.materials = materials

    def csg_model(self):
        surface1 = openmc.ZPlane(z0=self.width1*0.5, boundary_type="vacuum")
        surface2 = openmc.ZPlane(z0=self.width1*-0.5, boundary_type="vacuum")
        surface3 = openmc.XPlane(x0=self.width1*0.5, boundary_type="vacuum")
        surface4 = openmc.XPlane(x0=self.width1*-0.5, boundary_type="vacuum")
        surface5 = openmc.YPlane(x0=self.width1*0.5)
        surface6 = openmc.YPlane(x0=self.width1*-0.5, boundary_type="vacuum")
        surface7 = openmc.YPlane(x0=self.width1*0.5+self.width2, boundary_type="vacuum")

        region1 = -surface1 & +surface2 & -surface3 & +surface4
        region2 = -surface2
        region3 = -surface3
        region4 = -surface4
        region5 = -surface5
        region6 = -surface6
        region7 = -surface7

        cell = openmc.Cell(region=region)
        cell.fill = self.materials[0]
        geometry = openmc.Geometry([cell])
        model = openmc.Model(geometry=geometry)
        return model

    def cadquery_assembly(self):
        assembly = cq.Assembly(name="Cuboid")
        Cuboid = cq.Workplane().box(self.width, self.width, self.width)
        assembly.add(Cuboid)
        return assembly

    def export_stp_file(self, filename="Cuboid.step"):
        self.cadquery_assembly().save(filename, "STEP")

    def dagmc_model(self, filename="Cuboid.h5m", min_mesh_size=0.1, max_mesh_size=100.0):
        assembly = self.cadquery_assembly()
        ctd = CadToDagmc()
        material_tags = [self.materials[0].name]
        ctd.add_cadquery_object(assembly, material_tags=material_tags)
        ctd.export_dagmc_h5m_file(
            filename,
            min_mesh_size=min_mesh_size,
            max_mesh_size=max_mesh_size
        )
        universe = openmc.DAGMCUniverse(filename).bounded_universe()
        geometry = openmc.Geometry(universe)
        model = openmc.Model(geometry=geometry)
        return model
