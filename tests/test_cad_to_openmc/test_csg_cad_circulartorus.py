from model_benchmark_zoo import Circulartorus
import openmc
import math
import numpy as np
def test_compare():
    # single material used in both simulations
    mat1 = openmc.Material(name='1')
    mat1.add_nuclide('Fe56', 1)
    mat1.set_density('g/cm3', 1)
    my_materials = openmc.Materials([mat1])

    # geometry used in both simulations
    major_radius = 10
    minor_radius = 4
    common_geometry_object = Circulartorus(materials=my_materials, major_radius=major_radius, minor_radius=minor_radius)
    # just writing a CAD step file for visulisation
    common_geometry_object.export_stp_file("circulartorus.stp")

    mat_filter = openmc.MaterialFilter(mat1)
    tally = openmc.Tally(name='mat1_flux_tally')
    tally.filters = [mat_filter]
    tally.scores = ['flux']
    my_tallies = openmc.Tallies([tally])

    my_settings = openmc.Settings()
    my_settings.batches = 10
    my_settings.inactive = 0
    my_settings.particles = 500
    my_settings.run_mode = 'fixed source'

    # Create a DT point source
    my_source = openmc.Source()
    r = openmc.stats.Discrete([major_radius], [1])
    phi = openmc.stats.Uniform(0, 2*np.pi)
    z = openmc.stats.Discrete([0], [1])
    my_source.space = openmc.stats.CylindricalIndependent(r, phi, z)
    my_source.energy = openmc.stats.Discrete([14e6], [1])
    my_settings.source = my_source

    # making openmc.Model with CSG geometry
    csg_model = common_geometry_object.csg_model()
    csg_model.materials = my_materials
    csg_model.tallies = my_tallies
    csg_model.settings = my_settings

    output_file_from_csg = csg_model.run()

    # extracting the tally result from the CSG simulation
    with openmc.StatePoint(output_file_from_csg) as sp_from_csg:
        csg_result = sp_from_csg.get_tally(name="mat1_flux_tally")

    # making openmc.Model with DAGMC geometry and specifying mesh sizes to get a good representation of a circular torus
    dag_model = common_geometry_object.dagmc_model_with_cad_to_openmc()
    dag_model.materials = my_materials
    dag_model.tallies = my_tallies
    dag_model.settings = my_settings

    output_file_from_cad = dag_model.run()

    # extracting the tally result from the DAGMC simulation
    with openmc.StatePoint(output_file_from_cad) as sp_from_cad:
        cad_result = sp_from_cad.get_tally(name="mat1_flux_tally")
    
    assert math.isclose(cad_result.mean, csg_result.mean)

