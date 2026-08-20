import math

from .utils import BaseCommonGeometryObject

class _TwoAnnularSectorsBase(BaseCommonGeometryObject):
    """Two nested annular sectors sharing part of a curved surface.

    The second sector sits directly outside the first and is shorter than it, so
    the two solids meet over only part of the cylinder at the mid radius. How much
    of that cylinder is shared depends on the angle of the second sector, and the
    two subclasses cover the two cases that behave differently when imprinting.
    """

    def __init__(
        self,
        inner_radius,
        mid_radius,
        outer_radius,
        height,
        second_height,
        angle,
        second_angle,
    ):
        if not inner_radius < mid_radius < outer_radius:
            raise ValueError(
                "radii must satisfy inner_radius < mid_radius < outer_radius"
            )
        if second_height >= height:
            raise ValueError("second_height should be less than height")
        if not 0 < second_angle <= angle < 180:
            raise ValueError("angles must satisfy 0 < second_angle <= angle < 180")

        self.inner_radius = inner_radius
        self.mid_radius = mid_radius
        self.outer_radius = outer_radius
        self.height = height
        self.second_height = second_height
        self.angle = angle
        self.second_angle = second_angle

    @property
    def second_angle_start(self):
        """Angle at which the second sector starts, centred within the first."""
        return (self.angle - self.second_angle) / 2

    def analytic_volumes(self):
        """Exact volume of each sector, its annulus scaled by its arc."""
        return (
            math.pi * (self.mid_radius ** 2 - self.inner_radius ** 2)
            * self.height * self.angle / 360,
            math.pi * (self.outer_radius ** 2 - self.mid_radius ** 2)
            * self.second_height * self.second_angle / 360,
        )

    def _csg_model(self, materials):
        import openmc

        ri = self.inner_radius
        rm = self.mid_radius
        ro = self.outer_radius
        h = self.height
        h2 = self.second_height
        start = self.second_angle_start

        def radial_plane(degrees, boundary_type="transmission"):
            """Plane containing the z axis, rotated `degrees` from the xz plane.

            The positive side of the plane is the side at larger angles.
            """
            radians = math.radians(degrees)
            return openmc.Plane(
                a=-math.sin(radians),
                b=math.cos(radians),
                c=0.0,
                d=0.0,
                boundary_type=boundary_type,
            )

        inner_cyl = openmc.ZCylinder(r=ri)
        mid_cyl = openmc.ZCylinder(r=rm)
        outer_cyl = openmc.ZCylinder(r=ro, boundary_type="vacuum")
        z_top = openmc.ZPlane(z0=h / 2, boundary_type="vacuum")
        z_bot = openmc.ZPlane(z0=-h / 2, boundary_type="vacuum")
        z2_top = openmc.ZPlane(z0=h2 / 2)
        z2_bot = openmc.ZPlane(z0=-h2 / 2)

        sector_start = radial_plane(0, boundary_type="vacuum")
        sector_end = radial_plane(self.angle, boundary_type="vacuum")

        # When the second sector spans the full angle its radial faces coincide
        # with those of the first, so reuse the surfaces rather than duplicating.
        if self.second_angle == self.angle:
            second_start, second_end = sector_start, sector_end
        else:
            second_start = radial_plane(start)
            second_end = radial_plane(start + self.second_angle)


        # first sector: full height and full angle, between inner and mid radius
        region1 = (
            +inner_cyl & -mid_cyl & +z_bot & -z_top & +sector_start & -sector_end
        )
        # second sector: shorter, between mid and outer radius
        region2 = (
            +mid_cyl & -outer_cyl & +z2_bot & -z2_top & +second_start & -second_end
        )

        cell1 = openmc.Cell(region=region1, fill=materials[0])
        cell2 = openmc.Cell(region=region2, fill=materials[1])

        geometry = openmc.Geometry([cell1, cell2])
        my_materials = openmc.Materials(materials)
        model = openmc.Model(geometry=geometry, materials=my_materials)
        return model

    def cadquery_assembly(self):
        import cadquery as cq

        def sector(inner, outer, height, angle, start):
            """Annular sector spanning `angle` degrees, starting at `start` degrees."""
            ring = cq.Workplane("XY").cylinder(height, outer).cut(
                cq.Workplane("XY").cylinder(height + 2, inner)
            )
            big = outer * 3
            result = ring
            # Remove the half space below the start ray, then the one above the
            # end ray, leaving the wedge between them.
            for rotation in (start, start + angle + 180):
                half_space = cq.Workplane("XY").transformed(
                    offset=(0, -big / 2, 0)
                ).box(2 * big, big, height + 4)
                result = result.cut(
                    half_space.rotate((0, 0, 0), (0, 0, 1), rotation)
                )
            return result

        # Solids are added in the same order as the materials in csg_model, as
        # cad_to_dagmc assigns material_tags[i] to the i-th solid of the assembly.
        assembly = cq.Assembly(name=self.assembly_name)

        assembly.add(
            sector(self.inner_radius, self.mid_radius, self.height, self.angle, 0)
        )
        assembly.add(
            sector(
                self.mid_radius,
                self.outer_radius,
                self.second_height,
                self.second_angle,
                self.second_angle_start,
            )
        )
        return assembly

class TwoAnnularSectors(_TwoAnnularSectorsBase):
    """Two annular sectors meeting over a band of a shared curved surface.

    The second sector spans the same angle as the first but only half its height,
    so the contact patch is a band that reaches the angular edges of the first
    sector's outer face. The imprint edges run clean across that face, which every
    OCCT gluing option handles, so this is the control case for
    :class:`TwoAnnularSectorsPartialArc`.
    """

    assembly_name = "two_annular_sectors"

    def __init__(
        self,
        inner_radius=3,
        mid_radius=6,
        outer_radius=9,
        height=10,
        second_height=5,
        angle=90,
    ):
        super().__init__(
            inner_radius=inner_radius,
            mid_radius=mid_radius,
            outer_radius=outer_radius,
            height=height,
            second_height=second_height,
            angle=angle,
            second_angle=angle,
        )

class TwoAnnularSectorsPartialArc(_TwoAnnularSectorsBase):
    """Two annular sectors meeting over an island patch of a shared curved surface.

    The second sector is both shorter and narrower than the first, so the contact
    patch is strictly interior to the first sector's outer face and reaches its
    boundary in neither the axial nor the angular direction. Imprinting has to
    split the larger curved face around an island, which OCCT's "full" gluing
    cannot do: it returns the two solids with no shared face at all. The "partial"
    gluing used by CadQuery since CadQuery/cadquery#2069 handles it correctly.
    """

    assembly_name = "two_annular_sectors_partial_arc"

    def __init__(
        self,
        inner_radius=3,
        mid_radius=6,
        outer_radius=9,
        height=10,
        second_height=5,
        angle=90,
        second_angle=45,
    ):
        if second_angle >= angle:
            raise ValueError("second_angle should be less than angle")
        super().__init__(
            inner_radius=inner_radius,
            mid_radius=mid_radius,
            outer_radius=outer_radius,
            height=height,
            second_height=second_height,
            angle=angle,
            second_angle=second_angle,
        )
