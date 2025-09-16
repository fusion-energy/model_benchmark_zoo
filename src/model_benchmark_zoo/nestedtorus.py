from .utils import BaseCommonGeometryObject
import cadquery as cq
import openmc

class Nestedtorus(BaseCommonGeometryObject):
    """
    Creates a nested torus shape with a core torus and concentric torus shells.
    :param major_radius: The major radius of the tori.
    :param minor_radii: A list of minor radii for the tori, sorted in descending order.
    The number of shells will be len(minor_radii) - 1.
    """
    def __init__(self, major_radius=10, minor_radii=[4, 3, 2, 1]):
        if not all(i > j for i, j in zip(minor_radii, minor_radii[1:])):
            raise ValueError("minor_radii must be in descending order.")
        self.major_radius = major_radius
        self.minor_radii = minor_radii

    def csg_model(self, materials):
        """
        Creates an OpenMC CSG model of the nested torus.
        """
        if len(materials) < len(self.minor_radii):
            raise ValueError(f"Number of materials ({len(materials)}) must be at least equal to the number of minor radii ({len(self.minor_radii)}).")

        surfaces = [openmc.ZTorus(a=self.major_radius, b=r, c=r) for r in self.minor_radii]
        
        # Add vacuum boundary to the outermost surface
        surfaces[0].boundary_type = "vacuum"

        regions = []
        # Create the shells
        for i in range(len(self.minor_radii) - 1):
            region = +surfaces[i+1] & -surfaces[i]
            regions.append(region)
        
        # Create the core
        regions.append(-surfaces[-1])
        
        # Reverse regions to have from inside to outside
        regions.reverse()

        cells = []
        for i, region in enumerate(regions):
            cell = openmc.Cell(region=region)
            cell.fill = materials[i]
            cells.append(cell)
        
        geometry = openmc.Geometry(cells)
        my_materials = openmc.Materials(materials)
        model = openmc.Model(geometry=geometry, materials=my_materials)
        return model

    def cadquery_assembly(self):
        """
        Creates a CadQuery assembly of the nested torus.
        """
        assembly = cq.Assembly(name="nestedtorus")

        # Create the shells and the core
        for i in range(len(self.minor_radii)):
            if i == len(self.minor_radii) - 1:
                # This is the core
                core_torus = cq.Solid.makeTorus(self.major_radius, self.minor_radii[i])
                assembly.add(core_torus, name=f"torus_core")
            else:
                outer_torus = cq.Solid.makeTorus(self.major_radius, self.minor_radii[i])
                inner_torus = cq.Solid.makeTorus(self.major_radius, self.minor_radii[i+1])
                shell = outer_torus.cut(inner_torus)
                assembly.add(shell, name=f"torus_shell_{i}")
        
        return assembly
