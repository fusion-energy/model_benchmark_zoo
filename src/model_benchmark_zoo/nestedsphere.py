
class NestedSphere:
    def __init__(self, materials, radius1=10, radius2=5):
        self.radius1 = radius1
        self.radius2 = radius2
        self.materials = materials

    def csg_model(self):
        import openmc
        
        surface1 = openmc.Sphere(r=self.radius1)
        surface2 = openmc.Sphere(r=self.radius1+self.radius2, boundary_type="vacuum")
        region1 = -surface1
        region2 = +surface1 & -surface2
        cell1 = openmc.Cell(region=region1)
        cell1.fill = self.materials[0]
        cell2 = openmc.Cell(region=region2)
        cell2.fill = self.materials[1]
        geometry = openmc.Geometry([cell1, cell2])
        model = openmc.Model(geometry=geometry)
        return model

    def cadquery_assembly(self):
        import cadquery as cq
        assembly = cq.Assembly(name="nestedshpere")
        sphere1 = cq.Workplane().sphere(self.radius1)
        sphere2 = cq.Workplane().sphere(self.radius1 + self.radius2).cut(sphere1)
        assembly.add(sphere1)
        assembly.add(sphere2)
        return assembly

    def export_stp_file(self, filename="sphere.step"):
        self.cadquery_assembly().save(filename, "STEP")

    def dagmc_model(self, filename="nestedshpere.h5m", min_mesh_size=0.1, max_mesh_size=100.0):
        from cad_to_dagmc import CadToDagmc
        import openmc
        
        assembly = self.cadquery_assembly()
        ctd = CadToDagmc()
        material_tags = [self.materials[0].name, self.materials[1].name]
        ctd.add_cadquery_object(assembly, material_tags=material_tags)
        ctd.export_dagmc_h5m_file(
            filename=filename,
            min_mesh_size=min_mesh_size,
            max_mesh_size=max_mesh_size,
            msh_filename='nestedshpere.msh'  # this arg allows the gmsh file to be written out
        )
        universe = openmc.DAGMCUniverse(filename).bounded_universe()
        geometry = openmc.Geometry(universe)
        model = openmc.Model(geometry=geometry)
        return model

    def dagmc_model_with_cad_to_openmc(self, filename="nestedsphere.h5m"):
        from CAD_to_OpenMC import assembly
        import openmc

        self.export_stp_file()

        a=assembly.Assembly(["sphere.step"])
        a.verbose=2
        assembly.mesher_config['threads']=1
        a.run(
            backend='stl2',
            merge=True,
            h5m_filename=filename,
            sequential_tags=[self.materials[0].name, self.materials[1].name],
            scale=1.0
        )

        universe = openmc.DAGMCUniverse(filename, auto_geom_ids=True).bounded_universe()
        geometry = openmc.Geometry(universe)
        model = openmc.Model(geometry=geometry)
        return model
