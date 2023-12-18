
class Ellipticaltorus:
    def __init__(self, materials, major_radius=10, minor_radius1=2, minor_radius2=1):
        """
        input: minor_radius1 parallel to axis of revolution, minor_radius2 perpendicular to axis of revolution
        """
        self.materials = materials
        self.major_radius = major_radius
        self.minor_radius1 = minor_radius1
        self.minor_radius2 = minor_radius2

    def csg_model(self):
        import openmc

        surface = openmc.ZTorus(a=self.major_radius, b=self.minor_radius1, c=self.minor_radius2, boundary_type="vacuum")
    
        region = -surface
        cell = openmc.Cell(region=region)
        cell.fill = self.materials[0]
        materials = openmc.Materials([self.materials[0]])
        geometry = openmc.Geometry([cell])
        model = openmc.Model(geometry=geometry, materials=materials)
        return model

    def cadquery_assembly(self):
        import cadquery as cq
        assembly = cq.Assembly(name="ellipticaltorus")
        ellipticaltorus1 = cq.Workplane("XZ", origin=(self.major_radius, 0, 0)).ellipse(self.minor_radius2, self.minor_radius1).revolve(180, (-self.major_radius,0,0), (-self.major_radius,1,0))
        ellipticaltorus2 = cq.Workplane("XZ", origin=(-self.major_radius, 0, 0)).ellipse(self.minor_radius2, self.minor_radius1).revolve(180, (self.major_radius,0,0), (self.major_radius,1,0))
        ellipticaltorus = ellipticaltorus1.union(ellipticaltorus2)        
        assembly.add(ellipticaltorus)
        return assembly

    def export_stp_file(self, filename="ellipticaltorus.step"):
        self.cadquery_assembly().save(filename, "STEP")

    def dagmc_model(self, filename="ellipticaltorus.h5m", min_mesh_size=0.1, max_mesh_size=100.0):
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
