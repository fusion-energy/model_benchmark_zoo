from pathlib import Path

#     *----------*
#     |          |
#     |          |----*
#     |          |    |
#     |          |    |
#     |          |----*
#     |          |
#     *----------*

class TwoTouchingCuboids:
    def __init__(self, materials, width1=10, width2=4):
        self.width1 = width1
        self.width2 = width2
        self.materials = materials

    def csg_model(self):
        import openmc
        surface1 = openmc.ZPlane(z0=self.width1*0.5, boundary_type="vacuum")
        surface2 = openmc.ZPlane(z0=self.width1*-0.5, boundary_type="vacuum")
        surface3 = openmc.XPlane(x0=self.width1*0.5, boundary_type="vacuum")
        surface4 = openmc.XPlane(x0=self.width1*-0.5, boundary_type="vacuum")
        surface5 = openmc.YPlane(y0=self.width1*0.5)
        surface6 = openmc.YPlane(y0=self.width1*-0.5, boundary_type="vacuum")
        surface7 = openmc.YPlane(y0=self.width1*0.5+self.width2, boundary_type="vacuum")

        region1 = -surface1 & +surface2 & -surface3 & +surface4 & -surface5 & +surface6
        region2 = -surface1 & +surface2 & -surface3 & +surface4 & -surface7 & +surface5

        cell1 = openmc.Cell(region=region1)
        cell1.fill = self.materials[0]

        cell2 = openmc.Cell(region=region2)
        cell2.fill = self.materials[1]

        geometry = openmc.Geometry([cell1, cell2])
        materials = openmc.Materials([self.materials[0], self.materials[1]])
        model = openmc.Model(geometry=geometry, materials=materials)
        return model

    def cadquery_assembly(self):
        import cadquery as cq
        assembly = cq.Assembly(name="TwoTouchingCuboids")
        cuboid1 = cq.Workplane().box(self.width1, self.width1, self.width1)
        assembly.add(cuboid1)
        cuboid2 = cq.Workplane().moveTo(0.5*self.width1+ 0.5*self.width2).box(self.width2, self.width2, self.width2)
        assembly.add(cuboid2)
        return assembly

    def export_stp_file(self, filename="TwoTouchingCuboids.step"):
        self.cadquery_assembly().save(filename, "STEP")

    def dagmc_model_with_cad_to_dagmc(self, filename="TwoTouchingCuboids.h5m", min_mesh_size=0.1, max_mesh_size=100.0):
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
            msh_filename='TwoTouchingCuboids.msh'
        )
        universe = openmc.DAGMCUniverse(filename).bounded_universe()
        materials = openmc.Materials([self.materials[0], self.materials[1]])
        geometry = openmc.Geometry(universe)
        model = openmc.Model(geometry=geometry, materials=materials)
        return model

    def dagmc_model_with_cad_to_openmc(self, filename="TwoTouchingCuboids.h5m"):
        from CAD_to_OpenMC import assembly
        import openmc

        self.export_stp_file()

        a=assembly.Assembly(["TwoTouchingCuboids.step"])
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
        materials = openmc.Materials([self.materials[0], self.materials[1]])
        geometry = openmc.Geometry(universe)
        model = openmc.Model(geometry=geometry, materials=materials)
        return model
