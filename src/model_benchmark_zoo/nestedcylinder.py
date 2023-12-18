
class NestedCylinder:
    def __init__(self, materials, height1=15, height2=8, radius1=15, radius2=8):
        
        if height1<=height2:
            raise ValueError('height1 should be greater than height2')
        if radius1<=radius2:
            raise ValueError('radius1 should be greater than radius2')

        self.height1 = height1
        self.height2 = height2
        self.radius1 = radius1
        self.radius2 = radius2
        self.materials = materials

    def csg_model(self):
        import openmc
        
        surface_1 = openmc.ZCylinder(x0=0.0, y0=0.0, r=self.radius1, boundary_type="vacuum")
        surface_2 = openmc.ZPlane(z0=0.5*self.height1, boundary_type="vacuum")
        surface_3 = openmc.ZPlane(z0=-0.5*self.height1, boundary_type="vacuum")
    
        surface_3 = openmc.ZCylinder(x0=0.0, y0=0.0, r=self.radius2, boundary_type="vacuum")
        surface_4 = openmc.ZPlane(z0=0.5*self.height2, boundary_type="vacuum")
        surface_5 = openmc.ZPlane(z0=-0.5*self.height2, boundary_type="vacuum")
    
        region_1 = -surface_1 & -surface_2 & +surface_3
        region_2 = -surface_3 & -surface_4 & +surface_5

        cell_1 = openmc.Cell(region=region_1 & ~ region_2, fill=self.materials[0])
        cell_2 = openmc.Cell(region=region_2, fill=self.materials[1])

        geometry = openmc.Geometry([cell_1, cell_2])
        materials = openmc.Materials([self.materials[0], self.materials[1]])
        model = openmc.Model(geometry=geometry, materials=materials)
        return model

    def cadquery_assembly(self):
        import cadquery as cq
        assembly = cq.Assembly(name="cylinder")
        cylinder2 = cq.Workplane("XY", origin=(0, 0, 0)).circle(self.radius2).extrude(self.height2, both=True)
        cylinder1 = cq.Workplane("XY", origin=(0, 0, 0)).circle(self.radius1).extrude(self.height1, both=True).cut(cylinder2)
        assembly.add(cylinder1)
        assembly.add(cylinder2)
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
        materials = openmc.Materials([self.materials[0], self.materials[1]])
        model = openmc.Model(geometry=geometry, materials=materials)
        return model
