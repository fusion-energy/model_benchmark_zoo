from model_benchmark_zoo import Wedge
from model_benchmark_zoo.comparison import assert_tally_agreement, read_tally
import openmc

def test_compare():
    mat1 = openmc.Material(name='1')
    mat1.add_nuclide('Fe56', 1)
    mat1.set_density('g/cm3', 1)

    common_geometry_object = Wedge(base=3, height=10, depth=10)
    common_geometry_object.export_stp_file("wedge.stp")

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

    my_source = openmc.IndependentSource()
    my_source.space = openmc.stats.Point((1, 3, 0))
    my_source.angle = openmc.stats.Isotropic()
    my_source.energy = openmc.stats.Discrete([14e6], [1])
    my_settings.source = my_source

    csg_model = common_geometry_object.csg_model(materials=[mat1])
    csg_model.tallies = my_tallies
    csg_model.settings = my_settings

    output_file_from_csg = csg_model.run()

    with openmc.StatePoint(output_file_from_csg) as sp_from_csg:
        csg_result = read_tally(sp_from_csg, "mat1_flux_tally")

    common_geometry_object.export_h5m_file_with_cad_to_openmc(
        h5m_filename='wedge.h5m',
        material_tags=['1'],
    )
    dag_model = common_geometry_object.dagmc_model(
        h5m_filename='wedge.h5m',
        materials=[mat1]
    )
    dag_model.tallies = my_tallies
    dag_model.settings = my_settings

    output_file_from_cad = dag_model.run()

    with openmc.StatePoint(output_file_from_cad) as sp_from_cad:
        cad_result = read_tally(sp_from_cad, "mat1_flux_tally")

    assert_tally_agreement(cad_result, csg_result)
