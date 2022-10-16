
import cadquery as cq

class Sphere():

    def __init__(self, radius=10):
      self.radius = radius

    def openmc_cell(self):
        import openmc
        surface = openmc.sphere(radius=self.radius)
        region = -surface
        cell = openmc.cell(region=region)
        return cell

    def cadquery_shape(self):
        sphere = cq.Workplane().sphere(self.radius)
        return sphere

    def export_stp(self, filename='sphere.stp'):
        assembly = cq.Assembly(name="sphere")
        sphere = self.cadquery_shape()
        assembly.add(sphere)
        assembly.save(filename, exportType="STEP")
