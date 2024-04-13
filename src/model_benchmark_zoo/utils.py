
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

    def dagmc_model(self, h5m_filename: str, materials):
        import openmc

        if not Path(h5m_filename).exists():
            print(f'DAGMC h5m file with filename = {h5m_filename} not found, try making use of export_h5m_file first')
        universe = openmc.DAGMCUniverse(h5m_filename).bounded_universe()
        materials = openmc.Materials(materials)
        geometry = openmc.Geometry(universe)

        model = openmc.Model(geometry=geometry, materials=materials)
        return model