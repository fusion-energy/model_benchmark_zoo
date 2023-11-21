
class Cylinder:
    def __init__(self, materials, radius=10):
        self.materials = materials
        self.radius = radius

    def csg_model(self):
        import openmc

        surface_1 = openmc.ZCylinder(x0=0.0, y0=0.0, r=self.radius)
        surface_2 = openmc.ZPlane(z0=0.5*self.height)
        surface_3 = openmc.ZPlane(z0=-0.5*self.height)
    
        region = -surface_1 & -surface_2 & +surface_3
        cell = openmc.Cell(region=region)
        cell.fill = self.materials[0]
        geometry = openmc.Geometry([cell])
        model = openmc.Model(geometry=geometry)
        return model
    
    def cadquery_assembly(self):
        import cadquery as cq
        assembly = cq.Assembly(name="cylinder")
        cylinder = cq.Workplane("XY", origin=(0, 0, 0)).circle(self.radius).extrude(self.height, both=True)
        assembly.add(cylinder)
        return assembly

    def export_stp_file(self, filename="cylinder.step"):
        self.cadquery_assembly().save(filename, "STEP")

    def dagmc_model(self, filename="sphere.h5m", min_mesh_size=0.1, max_mesh_size=100.0):
        from cad_to_dagmc import CadToDagmc
        import openmc
        
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
