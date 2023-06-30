
import cadquery as cq
import openmc
from cad_to_dagmc import CadToDagmc

class Sphere():

    def __init__(self, radius=10):
      self.radius = radius

    def csg_model(self):
        import openmc
        surface = openmc.sphere(radius=self.radius, boundary_type='vacuum')
        region = -surface
        cell = openmc.cell(region=region)
        return cell

    def cadquery_assembly(self):
        assembly = cq.Assembly(name="sphere")
        sphere = cq.Workplane().sphere(self.radius)
        assembly.add(sphere)
        return assembly

    def stp_file(self, filename='sphere.step'):
        self.cadquery_assembly().save(filename)

    def dag_model(self, min_mesh_element_size=1)
        assembly = self.cadquery_assembly()
        ctd = CadToDagmc()
        ctd.add_cadquery_object(assembly)
        ctd.export_dagmc('sphere.h5m', min_mesh_element_size=1)
        dag_model = openmc.DAGMCUniverse('sphere.h5m').bounded_universe()
