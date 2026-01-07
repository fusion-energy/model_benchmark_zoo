
from pathlib import Path
from typing import Sequence

class BaseCommonGeometryObject:

    def export_stp_file(self, filename: str="common_geometry_object.step"):
        self.cadquery_assembly().save(filename, "STEP")

    def export_h5m_file_with_cad_to_dagmc(
        self,
        h5m_filename: str,
        material_tags: Sequence[str],
        min_mesh_size: float=0.1,
        max_mesh_size: float=100.0
    ):
        from cad_to_dagmc import CadToDagmc

        ctd = CadToDagmc()

        ctd.add_cadquery_object(
            cadquery_object=self.cadquery_assembly(),
            material_tags=material_tags,
            )
        ctd.export_dagmc_h5m_file(
            filename=h5m_filename,
            min_mesh_size=min_mesh_size,
            max_mesh_size=max_mesh_size,
        )

    def export_h5m_file_with_cad_to_openmc(
        self,
        h5m_filename: str,
        material_tags: Sequence[str],
    ):
        from CAD_to_OpenMC import assembly

        self.export_stp_file('tempory_file.step')  # todo put this is a temp folder
        a=assembly.Assembly(['tempory_file.step'])
        a.verbose=1
        assembly.mesher_config['threads']=1
        a.run(
            backend='stl2',
            merge=True,
            h5m_filename=h5m_filename,
            sequential_tags=material_tags,
            scale=1.0
        )

    def export_h5m_file_with_cadquery_direct_mesh_plugin(
        self,
        h5m_filename: str,
        material_tags: Sequence[str],
        tolerance: float=0.1,
        angular_tolerance: float=0.1
    ):
        import cadquery_direct_mesh_plugin
        import cad_to_dagmc
        
        assembly = self.cadquery_assembly()
        original_ids = cad_to_dagmc.get_ids_from_assembly(assembly)

        # both id lists should be the same length as each other and the same
        # length as the self.material_tags
        if len(original_ids) != len(material_tags):
            msg = f"Number of volumes {len(original_ids)} is not equal to number of material tags {len(material_tags)}"
            raise ValueError(msg)

        cq_mesh = assembly.toMesh(
            imprint=True,
            tolerance=tolerance,
            angular_tolerance=angular_tolerance,
            scale_factor=1.0,
            include_brep_edges=False,
            include_brep_vertices=False,
            parallel = True,
        )

        # Fix the material tag order for imprinted assemblies
        if cq_mesh["imprinted_assembly"] is not None:
            imprinted_solids_with_org_id = cq_mesh[
                "imprinted_solids_with_orginal_ids"
            ]

            scrambled_ids = cad_to_dagmc.get_ids_from_imprinted_assembly(
                imprinted_solids_with_org_id
            )

            material_tags_in_brep_order = cad_to_dagmc.order_material_ids_by_brep_order(
                original_ids, scrambled_ids, material_tags
            )
        else:
            material_tags_in_brep_order = material_tags

        # this is in the cad-to-dagmc module but skipping this for the direct-mesh plugin as it works with a single assembly only
        # cad_to_dagmc.check_material_tags(material_tags_in_brep_order, parts)

        # Extract the mesh information to allow export to h5m from the direct-mesh result
        vertices = cq_mesh["vertices"]
        triangles_by_solid_by_face = cq_mesh["solid_face_triangle_vertex_map"]

        cad_to_dagmc.vertices_to_h5m(
            vertices=vertices,
            triangles_by_solid_by_face=triangles_by_solid_by_face,
            material_tags=material_tags_in_brep_order,
            h5m_filename=h5m_filename,
            # implicit_complement_material_tag=implicit_complement_material_tag, not used in test suit yet
        )

    def dagmc_model(self, h5m_filename: str, materials):
        import openmc

        if not Path(h5m_filename).exists():
            print(f'DAGMC h5m file with filename = {h5m_filename} not found, try making use of export_h5m_file first')
        universe = openmc.DAGMCUniverse(h5m_filename).bounded_universe()
        materials = openmc.Materials(materials)
        geometry = openmc.Geometry(universe)

        model = openmc.Model(geometry=geometry, materials=materials)
        return model