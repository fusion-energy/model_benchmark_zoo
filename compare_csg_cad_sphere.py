from .model.sphere import Sphere


# geometry used in both simulations
common_geometry_object = Sphere(10)
# just writing a CAD step file for visulisation
common_geometry_object.create_stp_file("sphere.stp")

# single material used in both simulations
mat1 = openmc.Material()
mat1.add_nuclide('Fe56', 1)
mat1.set_density('g/cm', 1)
materials = openmc.Material()


csg_model = common_geometry_object.csg_model()
csg_model.materials = materials
csg_model.tally = #TODO
csg_model.settings = #TOD

output_file_from_csg = csg_model.run()


dag_model = common_geometry_object.dagmc_model()
dag_model.material = materials
dag_model.tally = #TODO
dag_model.settings = #TODO

output_file_from_cad = dag_model.run()

plot = compare_spectra_tally_results(
    output_file_from_csg,
    output_file_from_cad
)

plot.savefig("sphere_spectra.png")

