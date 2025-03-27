from model_benchmark_zoo import Oktavian
import openmc
import math

mat1 = openmc.Material(name='1')
mat1.set_density("g/cm3", 1.223)
mat1.add_nuclide("Al27", 1)
# commented out material definitions are from original benchmark
# mat1.add_nuclide("Al27", 0.9975488, "ao")
# mat1.add_nuclide("Si28", 0.001329808, "ao")
# mat1.add_nuclide("Si29", 6.752131e-05, "ao")
# mat1.add_nuclide("Si30", 4.450956e-05, "ao")
# mat1.add_nuclide("Fe54", 5.651123e-05, "ao")
# mat1.add_nuclide("Fe56", 0.0008871055, "ao")
# mat1.add_nuclide("Fe57", 2.048713e-05, "ao")
# mat1.add_nuclide("Fe58", 2.726461e-06, "ao")
# mat1.add_nuclide("Cu63", 2.938581e-05, "ao")
# mat1.add_nuclide("Cu65", 1.309765e-05, "ao")

mat2 = openmc.Material(name='2')
mat2.set_density("g/cm3", 7.824)
mat2.add_nuclide("Fe56", 1)
# mat2.add_nuclide("Cr50", 0.00803825, "wo")
# mat2.add_nuclide("Cr52", 0.15501, "wo")
# mat2.add_nuclide("Cr53", 0.0175768, "wo")
# mat2.add_nuclide("Cr54", 0.00437525, "wo")
# mat2.add_nuclide("Fe54", 0.0411488, "wo")
# mat2.add_nuclide("Fe56", 0.645948, "wo")
# mat2.add_nuclide("Fe57", 0.0149178, "wo")
# mat2.add_nuclide("Fe58", 0.00198528, "wo")
# mat2.add_nuclide("Ni58", 0.0755655, "wo")
# mat2.add_nuclide("Ni60", 0.0291075, "wo")
# mat2.add_nuclide("Ni61", 0.0012654, "wo")
# mat2.add_nuclide("Ni62", 0.00403374, "wo")
# mat2.add_nuclide("Ni64", 0.00102786, "wo")

my_materials = openmc.Materials([mat1, mat2])

# geometry used in both simulations
common_geometry_object = Oktavian()
# just writing a CAD step file for visulisation
common_geometry_object.export_stp_file("oktavian.stp")

mat1_filter = openmc.MaterialFilter(mat1)
tally1 = openmc.Tally(name='mat1_flux_tally')
tally1.filters = [mat1_filter]
tally1.scores = ['flux']

my_tallies = openmc.Tallies([tally1])

my_settings = openmc.Settings()
my_settings.batches = 10
my_settings.inactive = 0
my_settings.particles = 500
my_settings.run_mode = 'fixed source'

# Create a DT point source
my_source = openmc.IndependentSource()
my_source.space = openmc.stats.Point((0, 0, 0))
my_source.angle = openmc.stats.Isotropic()
my_source.energy = openmc.stats.Discrete([14e6], [1])
my_settings.source = my_source

# making openmc.Model with CSG geometry
csg_model = common_geometry_object.csg_model(materials=my_materials)
csg_model.tallies = my_tallies
csg_model.settings = my_settings

output_file_from_csg = csg_model.run()

# extracting the tally result from the CSG simulation
with openmc.StatePoint(output_file_from_csg) as sp_from_csg:
    csg_result = sp_from_csg.get_tally(name="mat1_flux_tally")
csg_result = f'CSG tally mean {csg_result.mean} std dev {csg_result.std_dev}'

common_geometry_object.export_h5m_file_with_cad_to_dagmc(
    h5m_filename='oktavian.h5m',
    material_tags=['1', '2'],
    # the small mesh sizes make a large detailed mesh which is needed to get similar answers
    min_mesh_size=0.01,
    max_mesh_size=0.5
)

# making openmc.Model with DAGMC geometry and specifying mesh sizes to get a good representation of a sphere
dag_model = common_geometry_object.dagmc_model(h5m_filename='oktavian.h5m', materials=[mat1, mat2])
dag_model.tallies = my_tallies
dag_model.settings = my_settings

output_file_from_cad = dag_model.run()

# extracting the tally result from the DAGMC simulation
with openmc.StatePoint(output_file_from_cad) as sp_from_cad:
    cad_result = sp_from_cad.get_tally(name="mat1_flux_tally")
cad_result = f'CAD tally mean {cad_result.mean} std dev {cad_result.std_dev}'

# printing both tally results
print(csg_result)
print(cad_result)
