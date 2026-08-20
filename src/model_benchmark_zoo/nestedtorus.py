import math

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

    def analytic_volumes(self):
        """Exact volume of the core and of each toroidal shell outside it."""
        volumes = []
        previous = 0.0
        for minor_radius in sorted(self.minor_radii):
            volumes.append(
                2 * math.pi ** 2 * self.major_radius
                * (minor_radius ** 2 - previous ** 2)
            )
            previous = minor_radius
        return tuple(volumes)

    def _csg_model(self, materials):
        """
        Creates an OpenMC CSG model of the nested torus.
        """
        if len(materials) < len(self.minor_radii):
            raise ValueError(f"Number of materials ({len(materials)}) must be at least equal to the number of minor radii ({len(self.minor_radii)}).")

        surfaces = [openmc.ZTorus(a=self.major_radius, b=r, c=r) for r in self.minor_radii]

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

        # Solids are added in the same order as the materials in csg_model, as
        # cad_to_dagmc assigns material_tags[i] to the i-th solid of the assembly.
        # csg_model reverses its regions so they run from the inside out, so the
        # core is added first and then each shell working outwards.
        core_torus = cq.Solid.makeTorus(self.major_radius, self.minor_radii[-1])
        assembly.add(core_torus, name=f"torus_core")

        for i in range(len(self.minor_radii) - 2, -1, -1):
            outer_torus = cq.Solid.makeTorus(self.major_radius, self.minor_radii[i])
            inner_torus = cq.Solid.makeTorus(self.major_radius, self.minor_radii[i+1])
            shell = outer_torus.cut(inner_torus)
            assembly.add(shell, name=f"torus_shell_{i}")

        return assembly
