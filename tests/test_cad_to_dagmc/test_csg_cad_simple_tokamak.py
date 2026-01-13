from model_benchmark_zoo import SimpleTokamak
import openmc
import math
import pytest

kwargs_options = [{'min_mesh_size': 0.05,
        'max_mesh_size': 5},
        {'tolerance': 0.1,
        'angular_tolerance': 0.1,},]

@pytest.mark.parametrize('kwargs', kwargs_options)
def test_compare(kwargs):
    # single material used in both simulations
    mat1 = openmc.Material(name='1')
    mat1.add_nuclide('Fe56', 1)
    mat1.set_density('g/cm3', 1)

    mat2 = openmc.Material(name='2')
    mat2.add_nuclide('Be9', 1)
    mat2.set_density('g/cm3', 1)

    # geometry used in both simulations
    common_geometry_object = SimpleTokamak(
        radius=500,
        blanket_thicknesses=100,
        center_column_thicknesses=50
    )

    mat1_filter = openmc.MaterialFilter(mat1)
    tally1 = openmc.Tally(name='mat1_flux_tally')
    tally1.filters = [mat1_filter]
    tally1.scores = ['flux']

    mat2_filter = openmc.MaterialFilter(mat2)
    tally2 = openmc.Tally(name='mat2_flux_tally')
    tally2.filters = [mat2_filter]
    tally2.scores = ['flux']

    my_tallies = openmc.Tallies([tally1, tally2])

    my_settings = openmc.Settings()
    my_settings.batches = 10
    my_settings.inactive = 0
    my_settings.particles = 500
    my_settings.run_mode = 'fixed source'

    # Create a DT ring source
    my_source = openmc.IndependentSource()
    source_r = common_geometry_object.center_column_thicknesses + (common_geometry_object.radius-common_geometry_object.center_column_thicknesses) /2
    r = openmc.stats.Discrete([source_r], [1])
    phi = openmc.stats.Uniform(0, 2*math.pi)
    z = openmc.stats.Discrete([0], [1])
    my_source.space = openmc.stats.CylindricalIndependent(r, phi, z)
    my_source.energy = openmc.stats.Discrete([14e6], [1])
    my_settings.source = my_source

    # making openmc.Model with CSG geometry
    csg_model = common_geometry_object.csg_model(materials=[mat1, mat2])
    csg_model.tallies = my_tallies
    csg_model.settings = my_settings

    output_file_from_csg = csg_model.run()

    # extracting the tally result from the CSG simulation
    with openmc.StatePoint(output_file_from_csg) as sp_from_csg:
        csg_result_mat_1 = sp_from_csg.get_tally(name="mat1_flux_tally")
        csg_result_mat_2 = sp_from_csg.get_tally(name="mat2_flux_tally")

    common_geometry_object.export_h5m_file_with_cad_to_dagmc(
        filename='simpletokamak.h5m',
        material_tags=['1', '2'],
        **kwargs
    )
    # making openmc.Model with DAGMC geometry and specifying mesh sizes to get a good representation of a sphere
    dag_model = common_geometry_object.dagmc_model(h5m_filename='simpletokamak.h5m', materials=[mat1, mat2])
    dag_model.tallies = my_tallies
    dag_model.settings = my_settings

    output_file_from_cad = dag_model.run()

    # extracting the tally result from the DAGMC simulation
    with openmc.StatePoint(output_file_from_cad) as sp_from_cad:
        cad_result_mat_1 = sp_from_cad.get_tally(name="mat1_flux_tally")
        cad_result_mat_2 = sp_from_cad.get_tally(name="mat2_flux_tally")

    assert math.isclose(cad_result_mat_1.mean.flatten()[0].flatten()[0], csg_result_mat_1.mean.flatten()[0].flatten()[0], rel_tol=0.01)
    assert math.isclose(cad_result_mat_2.mean.flatten()[0].flatten()[0], csg_result_mat_2.mean.flatten()[0].flatten()[0], rel_tol=0.01)
