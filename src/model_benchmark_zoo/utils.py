
from pathlib import Path
from typing import Sequence

#: Distance between the geometry and the vacuum boundary, in cm. The CSG and the
#: CAD model are both enclosed in a box this far outside their shared bounding
#: box, so the two describe the same transport problem.
BOUNDING_BOX_PADDING = 1.0


class BaseCommonGeometryObject:
    """Base class giving every model a CSG and a CAD form of the same geometry.

    Subclasses implement ``_csg_model`` and ``cadquery_assembly``. The CSG model
    they build is the geometry on its own; this class is what encloses it in the
    padded void box that :meth:`dagmc_model` gives the CAD side, so that neither
    side has to reason about where the vacuum boundary belongs.
    """

    def export_stp_file(self, filename: str="common_geometry_object.step"):
        self.cadquery_assembly().save(filename, "STEP")

    def cad_bounding_box(self):
        """Return the exact bounding box of the CadQuery solids.

        CadQuery computes this with ``BRepBndLib.AddOptimal``, so it is exact
        rather than a triangulated estimate, and it is always finite.

        Returns:
            The lower left and upper right corners as two numpy arrays.
        """
        import numpy as np

        boxes = []
        for shape, _, location, _ in self.cadquery_assembly():
            moved = shape.moved(location) if hasattr(shape, "moved") else shape
            boxes.append(moved.BoundingBox())
        return (np.array([min(b.xmin for b in boxes),
                          min(b.ymin for b in boxes),
                          min(b.zmin for b in boxes)]),
                np.array([max(b.xmax for b in boxes),
                          max(b.ymax for b in boxes),
                          max(b.zmax for b in boxes)]))

    def bounding_box(self):
        """Return the padded bounding box shared by the CSG and the CAD model.

        The extent comes from the CadQuery solids. OpenMC cannot be used for it,
        because it propagates bounding boxes one surface at a time and so cannot
        work out that truncating an infinite surface also bounds it sideways: a
        cone cut by two planes is reported as bounded in z but infinite in x and
        y, and a torus sector is reported as the whole torus. The CAD extent has
        neither problem, being exact and always finite, and it is the geometry
        the DAGMC mesh is built from.

        This is only safe because :meth:`csg_model` keeps the filled cells alone.
        A void cell is free to reach anywhere, and several models used to define
        one that did, so a box drawn round the solids would have cut through it.

        Returns:
            The lower left and upper right corners as two tuples of floats.
        """
        lower, upper = self.cad_bounding_box()
        return (tuple(lower - BOUNDING_BOX_PADDING),
                tuple(upper + BOUNDING_BOX_PADDING))

    def _bounding_surface(self):
        import openmc

        lower, upper = self.bounding_box()
        return openmc.model.RectangularParallelepiped(
            lower[0], upper[0], lower[1], upper[1], lower[2], upper[2],
            boundary_type="vacuum"
        )

    def csg_model(self, materials):
        """Return the CSG model enclosed in the padded void box.

        The geometry built by ``_csg_model`` is surrounded by a void region out
        to the bounding box, and the vacuum boundary is moved onto that box.
        Leaving the vacuum boundary on the geometry's own surface would kill
        particles that a non-convex shape lets back in, for example one that
        leaves the inner surface of a torus and crosses the hole, which the CAD
        model transports because it has the same void region around it.

        Only the filled cells are carried over. Any void cell a model happens to
        define is dropped, because everything the filled cells do not claim ends
        up in the surrounding void anyway, whether it is a cavity inside the
        geometry or the space around it. Dropping them also keeps the bounding
        box tied to the solids, since a void cell is free to reach anywhere.

        Args:
            materials: materials to fill the model's cells with.

        Returns:
            An ``openmc.Model`` whose only vacuum boundary is the bounding box.
        """
        import openmc

        model = self._csg_model(materials)
        geometry = model.geometry

        for surface in geometry.get_all_surfaces().values():
            if surface.boundary_type == "vacuum":
                surface.boundary_type = "transmission"

        cells = [c for c in geometry.get_all_cells().values() if c.fill is not None]
        occupied = cells[0].region
        for cell in cells[1:]:
            occupied = occupied | cell.region

        boundary = self._bounding_surface()
        surrounding_void = openmc.Cell(region=-boundary & ~occupied)

        return openmc.Model(
            geometry=openmc.Geometry(cells + [surrounding_void]),
            materials=model.materials,
        )

    def export_h5m_file_with_cad_to_dagmc(
        self,
        material_tags,
        **kwargs
    ):
        from cad_to_dagmc import CadToDagmc

        ctd = CadToDagmc()

        ctd.add_cadquery_object(
            cadquery_object=self.cadquery_assembly(),
            material_tags=material_tags,
            )
        ctd.export_dagmc_h5m_file(**kwargs)

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
        """Return the DAGMC model enclosed in the padded void box.

        The box is the one :meth:`bounding_box` builds for the CSG model rather
        than the one ``bounded_universe`` would derive from the faceted geometry.
        A faceted surface generally sits just inside the analytic one, so letting
        each side measure its own extent would leave the two boxes differing by
        the faceting error. Using the same box on both sides makes even an
        unfiltered flux tally comparable, since the void either side scores is
        then the same volume.

        Args:
            h5m_filename: DAGMC file to fill the bounding cell with.
            materials: materials the model's volumes are filled with.

        Returns:
            An ``openmc.Model`` bounded identically to :meth:`csg_model`.
        """
        import openmc

        if not Path(h5m_filename).exists():
            print(f'DAGMC h5m file with filename = {h5m_filename} not found, try making use of export_h5m_file first')

        boundary = self._bounding_surface()
        bounding_cell = openmc.Cell(
            fill=openmc.DAGMCUniverse(h5m_filename), region=-boundary
        )
        geometry = openmc.Geometry(openmc.Universe(cells=[bounding_cell]))

        model = openmc.Model(geometry=geometry, materials=openmc.Materials(materials))
        return model