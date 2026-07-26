from model_benchmark_zoo import TwoAnnularSectorsPartialArc
from model_benchmark_zoo.comparison import read_tally
import openmc

# two materials used in both simulations
mat1 = openmc.Material(name='1')
mat1.add_nuclide('Fe56', 1)
mat1.set_density('g/cm3', 1)

mat2 = openmc.Material(name='2')
mat2.add_nuclide('Be9', 1)
mat2.set_density('g/cm3', 1)

my_materials = openmc.Materials([mat1, mat2])

# geometry used in both simulations
common_geometry_object = TwoAnnularSectorsPartialArc(
    inner_radius=3, mid_radius=6, outer_radius=9, height=10, second_height=5, angle=90, second_angle=45
)
# just writing a CAD step file for visulisation
common_geometry_object.export_stp_file("two_annular_sectors_partial_arc.stp")

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

# Create a DT point source inside the first sector
my_source = openmc.IndependentSource()
my_source.space = openmc.stats.Point((3.182, 3.182, 0))
my_source.angle = openmc.stats.Isotropic()
my_source.energy = openmc.stats.Discrete([14e6], [1])
my_settings.source = my_source

# making openmc.Model with CSG geometry
csg_model = common_geometry_object.csg_model(materials=[mat1, mat2])
csg_model.tallies = my_tallies
csg_model.settings = my_settings

output_file_from_csg = csg_model.run()

# extracting the tally result from the CSG simulation
with openmc.StatePoint(output_file_from_csg) as sp_from_csg:
    csg_result_mat_1 = read_tally(sp_from_csg, "mat1_flux_tally")
    csg_result_mat_2 = read_tally(sp_from_csg, "mat2_flux_tally")

# making openmc.Model with DAGMC geometry
common_geometry_object.export_h5m_file_with_cad_to_dagmc(
    filename='two_annular_sectors_partial_arc.h5m',
    material_tags=['1', '2'],
    min_mesh_size=0.01,
    max_mesh_size=0.5
)
dag_model = common_geometry_object.dagmc_model(
    h5m_filename='two_annular_sectors_partial_arc.h5m',
    materials=[mat1, mat2]
)
dag_model.tallies = my_tallies
dag_model.settings = my_settings

output_file_from_cad = dag_model.run()

# extracting the tally result from the DAGMC simulation
with openmc.StatePoint(output_file_from_cad) as sp_from_cad:
    cad_result_mat_1 = read_tally(sp_from_cad, "mat1_flux_tally")
    cad_result_mat_2 = read_tally(sp_from_cad, "mat2_flux_tally")

# printing both tally results
print(f'CSG tally mat1 mean {csg_result_mat_1.mean} std dev {csg_result_mat_1.std_dev}')
print(f'CAD tally mat1 mean {cad_result_mat_1.mean} std dev {cad_result_mat_1.std_dev}')
print(f'CSG tally mat2 mean {csg_result_mat_2.mean} std dev {csg_result_mat_2.std_dev}')
print(f'CAD tally mat2 mean {cad_result_mat_2.mean} std dev {cad_result_mat_2.std_dev}')
