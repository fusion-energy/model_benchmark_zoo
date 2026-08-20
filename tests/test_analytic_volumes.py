"""Check every model's CAD solids against its analytic volumes.

This needs cadquery only, not a mesher or a transport code, so it is cheap enough to
be the first thing that runs and it fails immediately if a model's two descriptions
have drifted apart.
"""

import math

import pytest
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps

import model_benchmark_zoo as zoo
from model_benchmark_zoo.utils import BaseCommonGeometryObject

#: Models with no closed form volume. The two assemblies are built from revolved
#: profiles, and the sphere with three bores has overlaps between the bores that do
#: not reduce to a standard solid.
WITHOUT_ANALYTIC_VOLUMES = {
    "Oktavian",
    "SimpleTokamak",
    "SphereWithMultipleHoles",
}

#: Largest relative difference tolerated between a CAD solid and its formula. The
#: solids are the analytic geometry rather than a mesh of it, so the only difference
#: expected is in how tightly OCCT integrates the volume, which on a B-spline or a
#: revolved face is well above floating point noise.
RELATIVE_TOLERANCE = 1e-6

#: Tolerance the volume integral is taken to. OCCT's default is loose enough to cost
#: a fraction of a percent on a revolved face, which is the same size as the faceting
#: error these volumes exist to measure.
INTEGRATION_TOLERANCE = 1e-11


def model_classes():
    return sorted(
        name for name in dir(zoo)
        if isinstance(getattr(zoo, name), type)
        and issubclass(getattr(zoo, name), BaseCommonGeometryObject)
        and getattr(zoo, name) is not BaseCommonGeometryObject
        and not name.startswith("_")
    )


def cad_solids(assembly):
    solids = []
    for child in assembly.objects.values():
        if getattr(child, "obj", None) is None:
            continue
        obj = child.obj
        solids.append(obj.val() if hasattr(obj, "val") else obj)
    return solids


def precise_volume(shape):
    properties = GProp_GProps()
    BRepGProp.VolumeProperties_s(
        shape.wrapped, properties, INTEGRATION_TOLERANCE, True, True
    )
    return properties.Mass()


@pytest.mark.parametrize("name", model_classes())
def test_analytic_volumes_match_the_cad_solids(name):
    common_geometry_object = getattr(zoo, name)()
    volumes = common_geometry_object.analytic_volumes()

    if name in WITHOUT_ANALYTIC_VOLUMES:
        assert volumes is None, (
            f"{name} is listed as having no closed form volume but now returns one, "
            f"so it should be taken off WITHOUT_ANALYTIC_VOLUMES"
        )
        pytest.skip(f"{name} has no closed form volume")

    assert volumes is not None, (
        f"{name} has no analytic_volumes; add one, or add it to "
        f"WITHOUT_ANALYTIC_VOLUMES with a reason"
    )

    solids = cad_solids(common_geometry_object.cadquery_assembly())
    assert len(volumes) == len(solids), (
        f"{name} gives {len(volumes)} analytic volumes for {len(solids)} solids"
    )

    for index, (solid, expected) in enumerate(zip(solids, volumes)):
        actual = precise_volume(solid)
        assert actual == pytest.approx(expected, rel=RELATIVE_TOLERANCE), (
            f"{name} solid {index}: CAD volume {actual!r} against analytic "
            f"{expected!r}"
        )


@pytest.mark.parametrize("name", model_classes())
def test_analytic_volumes_are_positive_and_finite(name):
    volumes = getattr(zoo, name)().analytic_volumes()
    if volumes is None:
        pytest.skip(f"{name} has no closed form volume")

    assert isinstance(volumes, tuple), (
        f"{name} should return a tuple so the volumes cannot be mutated in place"
    )
    for index, volume in enumerate(volumes):
        # An all planar model with integral dimensions gives an exact int, which is
        # as good a volume as a float, so only the value is checked here.
        assert volume > 0, f"{name} volume {index} is not positive"
        assert math.isfinite(volume), f"{name} volume {index} is not finite"
