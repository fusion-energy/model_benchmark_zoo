from .utils import BaseCommonGeometryObject

class CylinderInBox(BaseCommonGeometryObject):
    def __init__(self, box_width=12, cylinder_radius=3, cylinder_height=10):
        self.box_width = box_width
        self.cylinder_radius = cylinder_radius
        self.cylinder_height = cylinder_height

    def csg_model(self, materials):
        import openmc

        w = self.box_width
        r = self.cylinder_radius
        ch = self.cylinder_height

        box = openmc.model.RectangularParallelepiped(
            -w / 2, w / 2, -w / 2, w / 2, -w / 2, w / 2,
            boundary_type="vacuum"
        )
        cyl = openmc.ZCylinder(r=r)
        z_cyl_top = openmc.ZPlane(z0=ch / 2)
        z_cyl_bot = openmc.ZPlane(z0=-ch / 2)

        # Cylinder region inside the box
        region_cyl = -cyl & +z_cyl_bot & -z_cyl_top

        # Box minus cylinder
        region_box = -box & ~region_cyl

        cell_cyl = openmc.Cell(region=region_cyl, fill=materials[0])
        cell_box = openmc.Cell(region=region_box, fill=materials[1])

        geometry = openmc.Geometry([cell_cyl, cell_box])
        my_materials = openmc.Materials(materials)
        model = openmc.Model(geometry=geometry, materials=my_materials)
        return model

    def cadquery_assembly(self):
        import cadquery as cq

        w = self.box_width
        r = self.cylinder_radius
        ch = self.cylinder_height

        assembly = cq.Assembly(name="cylinder_in_box")

        box = cq.Workplane("XY").box(w, w, w)
        cyl = cq.Workplane("XY").cylinder(ch, r)
        box_shell = box.cut(cyl)

        assembly.add(cyl)
        assembly.add(box_shell)
        return assembly
