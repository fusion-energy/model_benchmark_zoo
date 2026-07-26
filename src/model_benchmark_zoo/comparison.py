"""Comparison of CAD (DAGMC) tally results against their CSG reference.

Both the CSG and the CAD run of a model write ``statepoint.10.h5`` into the working
directory, and OpenMC reads tally results lazily from that file. A tally handle taken
from the first statepoint therefore returns the second run's numbers once the file has
been overwritten, which silently turns a comparison into a self-comparison. Use
:func:`read_tally` to read the values while the statepoint is still open.
"""

import math
from typing import NamedTuple

#: Largest relative difference tolerated between the CAD and CSG means. The CAD
#: geometry is faceted before transport, so a small systematic difference against the
#: analytic CSG surfaces is expected and does not indicate a broken model.
RELATIVE_TOLERANCE = 0.02

#: Largest difference tolerated in units of the combined Monte Carlo uncertainty.
SIGMA_TOLERANCE = 3.0


class TallyResult(NamedTuple):
    """A tally mean and its standard deviation, already read from the statepoint."""

    mean: float
    std_dev: float


def read_tally(statepoint, name: str, index: int = 0) -> TallyResult:
    """Read a named tally's mean and standard deviation from an open statepoint.

    Args:
        statepoint: an open ``openmc.StatePoint``.
        name: name of the tally to read.
        index: index into the flattened tally results.

    Returns:
        The mean and standard deviation as plain floats, read eagerly so that they
        cannot later be re-read from a statepoint file that another run has replaced.
    """
    tally = statepoint.get_tally(name=name)
    return TallyResult(
        float(tally.mean.flatten()[index]),
        float(tally.std_dev.flatten()[index]),
    )


def assert_tally_agreement(
    cad: TallyResult,
    csg: TallyResult,
    relative_tolerance: float = RELATIVE_TOLERANCE,
    sigma_tolerance: float = SIGMA_TOLERANCE,
) -> None:
    """Assert that a CAD tally agrees with its CSG reference.

    Two independent checks are applied and both must pass:

    1. Relative: the means agree to within ``relative_tolerance``. This caps the
       systematic difference introduced by faceting the CAD surfaces.
    2. Statistical: the means agree to within ``sigma_tolerance`` combined standard
       deviations. This catches a difference that is small in relative terms but far
       outside the Monte Carlo uncertainty of the two runs.

    Args:
        cad: result from the CAD (DAGMC) run.
        csg: result from the CSG run.
        relative_tolerance: largest permitted relative difference.
        sigma_tolerance: largest permitted difference in combined standard deviations.

    Raises:
        AssertionError: if either check fails.
    """
    difference = abs(cad.mean - csg.mean)
    combined_sigma = math.sqrt(cad.std_dev**2 + csg.std_dev**2)

    if difference == 0:
        return

    relative = difference / abs(csg.mean) if csg.mean else math.inf
    sigmas = difference / combined_sigma if combined_sigma else math.inf

    detail = (
        f"cad={cad.mean:.6g} +/- {cad.std_dev:.3g}, "
        f"csg={csg.mean:.6g} +/- {csg.std_dev:.3g}, "
        f"relative difference {relative:.3%} (limit {relative_tolerance:.3%}), "
        f"{sigmas:.2f} combined sigma (limit {sigma_tolerance})"
    )

    assert relative <= relative_tolerance, f"CAD and CSG differ systematically: {detail}"
    assert sigmas <= sigma_tolerance, f"CAD and CSG are statistically inconsistent: {detail}"
