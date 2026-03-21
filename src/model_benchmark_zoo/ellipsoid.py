from .utils import BaseCommonGeometryObject

class Ellipsoid(BaseCommonGeometryObject):
    def __init__(self, a=10, b=7, c=5):
        self.a = a
        self.b = b
        self.c = c

    def csg_model(self, materials):
        import openmc

        surface = openmc.Quadric(
            a=1 / self.a**2,
            b=1 / self.b**2,
            c=1 / self.c**2,
            k=-1,
        )
        bounding_sphere = openmc.Sphere(r=max(self.a, self.b, self.c) + 1, boundary_type="vacuum")

        region_material = -surface & -bounding_sphere
        region_void = +surface & -bounding_sphere

        cell1 = openmc.Cell(region=region_material, fill=materials[0])
        cell2 = openmc.Cell(region=region_void)

        geometry = openmc.Geometry([cell1, cell2])
        my_materials = openmc.Materials(materials)
        model = openmc.Model(geometry=geometry, materials=my_materials)
        return model

    def cadquery_assembly(self):
        import cadquery as cq
        from OCP.gp import gp_GTrsf, gp_Mat
        from OCP.BRepBuilderAPI import BRepBuilderAPI_GTransform

        sphere = cq.Solid.makeSphere(1.0)

        # Non-uniform scale to create ellipsoid with radii (a, b, c)
        gtrsf = gp_GTrsf()
        gtrsf.SetVectorialPart(
            gp_Mat(self.a, 0, 0, 0, self.b, 0, 0, 0, self.c)
        )
        builder = BRepBuilderAPI_GTransform(sphere.wrapped, gtrsf, True)
        builder.Build()
        ellipsoid_shape = cq.Shape(builder.Shape())

        assembly = cq.Assembly(name="ellipsoid")
        assembly.add(ellipsoid_shape)
        return assembly
