import cadquery as cq
import openmc
from cad_to_dagmc import CadToDagmc


class Sphere:
    def __init__(self, radius=10):
        self.radius = radius

    def csg_model(self):
        surface = openmc.sphere(radius=self.radius, boundary_type="vacuum")
        region = -surface
        cell = openmc.cell(region=region)
        # TODO return openmc.model object
        return cell

    def cadquery_assembly(self):
        assembly = cq.Assembly(name="sphere")
        sphere = cq.Workplane().sphere(self.radius)
        assembly.add(sphere)
        return assembly

    def stp_file(self, filename="sphere.step"):
        self.cadquery_assembly().save(filename)

    def dagmc_model(self, filename="sphere.h5m", min_mesh_size=1.0, max_mesh_size=100.0):
        assembly = self.cadquery_assembly()
        ctd = CadToDagmc()
        ctd.add_cadquery_object(assembly)
        ctd.export_dagmc_h5m_file(filename, min_mesh_size=min_mesh_size, max_mesh_size=min_mesh_element_size)
        dag_model = openmc.DAGMCUniverse(filename).bounded_universe()
        # TODO return openmc.model object
        return dag_model
