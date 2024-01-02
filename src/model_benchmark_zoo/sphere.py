
class Sphere:
    def __init__(self, materials, radius=10):
        self.radius = radius
        self.materials = materials

    def csg_model(self):
        import openmc

        surface = openmc.Sphere(r=self.radius, boundary_type="vacuum")
        region = -surface
        cell = openmc.Cell(region=region)
        cell.fill = self.materials[0]
        geometry = openmc.Geometry([cell])
        materials = openmc.Materials([self.materials[0]])
        model = openmc.Model(geometry=geometry, materials=materials)
        # TODO return openmc.model object
        return model

    def cadquery_assembly(self):
        import cadquery as cq
        assembly = cq.Assembly(name="sphere")
        sphere = cq.Workplane().sphere(self.radius)
        assembly.add(sphere)
        return assembly

    def export_stp_file(self, filename="sphere.step"):
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
        materials = openmc.Materials([self.materials[0]])
        geometry = openmc.Geometry(universe)
        model = openmc.Model(geometry=geometry, materials=materials)
        return model

    def dagmc_model_with_cad_to_openmc(self, filename="sphere.h5m"):
        from CAD_to_OpenMC import assembly
        import openmc

        self.export_stp_file()

        a=assembly.Assembly(["sphere.step"])
        a.verbose=0
        assembly.mesher_config['threads']=1
        a.run(
            backend='stl2',
            merge=True,
            h5m_filename=filename,
            sequential_tags=[self.materials[0].name],
            scale=1.0
        )

        universe = openmc.DAGMCUniverse(filename, auto_geom_ids=True).bounded_universe()
        geometry = openmc.Geometry(universe)
        model = openmc.Model(geometry=geometry)
        return model
