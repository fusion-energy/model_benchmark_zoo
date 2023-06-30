from .model.sphere import Sphere


# geometry used in both simulations
common_geometry_object = Sphere(10)

# single material used in both simulations
openmc.Material()


csg_model = common_geometry_object.csg_model
csg_model.material
csg_model.tally
csg_model.settings

output_file_from_csg = csg_model.run()


stp_filename = common_geometry_object.create_stp_file('sphere.stp')
stp_filename = common_geometry_object.dag_model(min_mesh_elelemt_size=1)


dag_model.material
dag_model.tally
dag_model.settings

output_file_from_cad = dag_model.run()

plot = compare_spectra_tally_results(output_file_from_csg, output_file_from_cad)

plot.savefig('sphere_')
