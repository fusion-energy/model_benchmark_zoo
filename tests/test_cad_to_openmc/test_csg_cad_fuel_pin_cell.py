from model_benchmark_zoo import FuelPinCell
import openmc
import math

def test_compare():
    mat1 = openmc.Material(name='1')
    mat1.add_nuclide('Fe56', 1)
    mat1.set_density('g/cm3', 1)

    mat2 = openmc.Material(name='2')
    mat2.add_nuclide('Be9', 1)
    mat2.set_density('g/cm3', 1)

    mat3 = openmc.Material(name='3')
    mat3.add_nuclide('Al27', 1)
    mat3.set_density('g/cm3', 1)

    common_geometry_object = FuelPinCell(fuel_radius=2, clad_outer_radius=2.5, pitch=8, height=10)
    common_geometry_object.export_stp_file("fuel_pin_cell.stp")

    mat1_filter = openmc.MaterialFilter(mat1)
    tally1 = openmc.Tally(name='mat1_flux_tally')
    tally1.filters = [mat1_filter]
    tally1.scores = ['flux']

    mat2_filter = openmc.MaterialFilter(mat2)
    tally2 = openmc.Tally(name='mat2_flux_tally')
    tally2.filters = [mat2_filter]
    tally2.scores = ['flux']

    mat3_filter = openmc.MaterialFilter(mat3)
    tally3 = openmc.Tally(name='mat3_flux_tally')
    tally3.filters = [mat3_filter]
    tally3.scores = ['flux']

    my_tallies = openmc.Tallies([tally1, tally2, tally3])

    my_settings = openmc.Settings()
    my_settings.batches = 10
    my_settings.inactive = 0
    my_settings.particles = 500
    my_settings.run_mode = 'fixed source'

    my_source = openmc.IndependentSource()
    my_source.space = openmc.stats.Point((0, 0, 0))
    my_source.angle = openmc.stats.Isotropic()
    my_source.energy = openmc.stats.Discrete([14e6], [1])
    my_settings.source = my_source

    csg_model = common_geometry_object.csg_model(materials=[mat1, mat2, mat3])
    csg_model.tallies = my_tallies
    csg_model.settings = my_settings

    output_file_from_csg = csg_model.run()

    with openmc.StatePoint(output_file_from_csg) as sp_from_csg:
        csg_result_mat_1 = sp_from_csg.get_tally(name="mat1_flux_tally")
        csg_result_mat_2 = sp_from_csg.get_tally(name="mat2_flux_tally")
        csg_result_mat_3 = sp_from_csg.get_tally(name="mat3_flux_tally")

    common_geometry_object.export_h5m_file_with_cad_to_openmc(
        h5m_filename='fuel_pin_cell.h5m',
        material_tags=['1', '2', '3'],
    )
    dag_model = common_geometry_object.dagmc_model(
        h5m_filename='fuel_pin_cell.h5m',
        materials=[mat1, mat2, mat3]
    )
    dag_model.tallies = my_tallies
    dag_model.settings = my_settings

    output_file_from_cad = dag_model.run()

    with openmc.StatePoint(output_file_from_cad) as sp_from_cad:
        cad_result_mat_1 = sp_from_cad.get_tally(name="mat1_flux_tally")
        cad_result_mat_2 = sp_from_cad.get_tally(name="mat2_flux_tally")
        cad_result_mat_3 = sp_from_cad.get_tally(name="mat3_flux_tally")

    assert math.isclose(cad_result_mat_1.mean.flatten()[0], csg_result_mat_1.mean.flatten()[0])
    assert math.isclose(cad_result_mat_2.mean.flatten()[0], csg_result_mat_2.mean.flatten()[0])
    assert math.isclose(cad_result_mat_3.mean.flatten()[0], csg_result_mat_3.mean.flatten()[0])
