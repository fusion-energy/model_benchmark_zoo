from model_benchmark_zoo import Nestedtorus
from model_benchmark_zoo.comparison import assert_tally_agreement, read_tally
import openmc
import numpy as np
import pytest

kwargs_options = [{'min_mesh_size': 0.01,
        'max_mesh_size': 0.5},
        {'tolerance': 0.1,
        'angular_tolerance': 0.1,},]

@pytest.mark.parametrize('kwargs', kwargs_options)
def test_compare(kwargs):
    # materials used in both simulations
    mat1 = openmc.Material(name='1')
    mat1.add_nuclide('Fe56', 1)
    mat1.set_density('g/cm3', 1)

    mat2 = openmc.Material(name='2')
    mat2.add_nuclide('Fe56', 1)
    mat2.set_density('g/cm3', 1)

    mat3 = openmc.Material(name='3')
    mat3.add_nuclide('Fe56', 1)
    mat3.set_density('g/cm3', 1)

    mat4 = openmc.Material(name='4')
    mat4.add_nuclide('Fe56', 1)
    mat4.set_density('g/cm3', 1)
    
    materials = [mat1, mat2, mat3, mat4]
    material_tags = ['1', '2', '3', '4']

    # geometry used in both simulations
    major_radius = 10
    minor_radii = [4,3,2,1]
    common_geometry_object = Nestedtorus(major_radius=major_radius, minor_radii=minor_radii)
    common_geometry_object.export_stp_file("nestedtorus.stp")

    # tallies used in both simulations, one per material. Filtering by material
    # keeps the comparison to the geometry itself. An unfiltered tally also scores
    # the void that bounded_universe leaves around the CAD geometry, which the CSG
    # model does not have, so the two sides would not be measuring the same thing.
    tallies = []
    for i, material in enumerate(materials):
        tally = openmc.Tally(name=f'mat{i + 1}_flux_tally')
        tally.filters = [openmc.MaterialFilter(material)]
        tally.scores = ['flux']
        tallies.append(tally)
    my_tallies = openmc.Tallies(tallies)

    my_settings = openmc.Settings()
    my_settings.batches = 10
    my_settings.inactive = 0
    my_settings.particles = 500
    my_settings.run_mode = 'fixed source'

    # Create a DT point source
    my_source = openmc.IndependentSource()
    r = openmc.stats.Discrete([major_radius], [1])
    phi = openmc.stats.Uniform(0, 2*np.pi)
    z = openmc.stats.Discrete([0], [1])
    my_source.space = openmc.stats.CylindricalIndependent(r, phi, z)
    my_source.energy = openmc.stats.Discrete([14e6], [1])
    my_settings.source = my_source

    # making openmc.Model with CSG geometry
    csg_model = common_geometry_object.csg_model(materials=materials)
    csg_model.tallies = my_tallies
    csg_model.settings = my_settings

    output_file_from_csg = csg_model.run()

    # extracting the tally result from the CSG simulation
    with openmc.StatePoint(output_file_from_csg) as sp_from_csg:
        csg_results = [
            read_tally(sp_from_csg, f"mat{i + 1}_flux_tally")
            for i in range(len(materials))
        ]

    # making openmc.Model with DAGMC geometry
    common_geometry_object.export_h5m_file_with_cad_to_dagmc(
        filename='nestedtorus.h5m',
        material_tags=material_tags,
        **kwargs
    )
    dag_model = common_geometry_object.dagmc_model(
        h5m_filename='nestedtorus.h5m',
        materials=materials
    )
    dag_model.tallies = my_tallies
    dag_model.settings = my_settings

    output_file_from_cad = dag_model.run()

    # extracting the tally result from the DAGMC simulation
    with openmc.StatePoint(output_file_from_cad) as sp_from_cad:
        cad_results = [
            read_tally(sp_from_cad, f"mat{i + 1}_flux_tally")
            for i in range(len(materials))
        ]
    
    for cad_result, csg_result in zip(cad_results, csg_results):
        assert_tally_agreement(cad_result, csg_result, relative_tolerance=0.05)
