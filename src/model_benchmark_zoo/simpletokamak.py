
class SimpleTokamak:
    def __init__(self, materials, radius=500, blanket_thicknesses=100, center_column_thicknesses=50):
        self.radius = radius
        self.blanket_thicknesses = blanket_thicknesses
        self.center_column_thicknesses = center_column_thicknesses
        self.materials = materials

    def csg_model(self):
        import openmc
        
        surface1 = openmc.Sphere(r=self.radius)
        surface2 = openmc.Sphere(r=self.radius + self.blanket_thicknesses, boundary_type="vacuum")
        surface3 = openmc.ZCylinder(r=self.center_column_thicknesses)
        
        region1 = -surface1 & +surface3  # plasma
        region2 = +surface1 & -surface2  # blanket
        region3 = -surface2 & -surface3  # center column

        cell1 = openmc.Cell(region=region1)
        cell2 = openmc.Cell(region=region2)
        cell2.fill = self.materials[1]
        cell3 = openmc.Cell(region=region3)
        cell3.fill = self.materials[2]

        geometry = openmc.Geometry([cell1, cell2, cell3])
        model = openmc.Model(geometry=geometry)
        return model

    def cadquery_assembly(self):
        import cadquery as cq
        assembly = cq.Assembly(name="simpletokamak")

        sphere_envelope = cq.Workplane().sphere(self.radius1 + self.blanket_thicknesses)

        center_column = cq.Workplane("XY").circle(self.radius).extrude(self.radius+self.blanket_thicknesses).intersect(sphere_envelope)

        sphere1 = cq.Workplane().sphere(self.radius1)
        sphere2 = cq.Workplane().sphere(self.radius1 + self.blanket_thicknesses).cut(sphere1).cut(center_column)
        assembly.add(sphere1)
        assembly.add(sphere2)
        return assembly

    def export_stp_file(self, filename="simpletokamak.step"):
        self.cadquery_assembly().save(filename, "STEP")

    def dagmc_model(self, filename="simpletokamak.h5m", min_mesh_size=0.1, max_mesh_size=100.0):
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
