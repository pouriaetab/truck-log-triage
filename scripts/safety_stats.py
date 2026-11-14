"""safety_stats.py: the few numbers a safety review needs, from ISO 26262 and plain statistics."""

import math


def e_class(share):
    """Exposure class (ISO 26262-3, Table B.2) from the share of driving time a situation takes."""
    # NOTE: why 0.10 and 0.01: Table B.2 puts E4 above 10% of driving time, E3 at 1% to 10%, E2 below 1%
    if share > 0.10:
        return "E4"
    if share >= 0.01:
        return "E3"
    if share > 0:
        return "E2"
    return "E1"  #  never seen in our data: very rare, or simply not in this sample


def asil(s, e, c):
    """ASIL from severity S0-S3, exposure E0-E4 and controllability C0-C3 (ISO 26262-3, Table 4)."""
    if min(s, e, c) == 0:
        return "QM"  # no inury, never happens, or everyone can control it: no ASIL
    # NOTE: why the sum works: in Table 4 one step up in S, E, or C moves the result one ASIL up,
    #       so S+E+C of 10 is D, 9 is C, 8 is B, 7 is A and 6 or less is QM (normal quality work).
    return {10: "D", 9: "C", 8: "B", 7: "A"}.get(s + e + c, "QM")


def wilson(k, n, z=1.96):
    """95% range for a share k out of n (Wilson): stays between 0 and 1 and works for small n."""
    # NOTE: why z=1.96: 95% of a bell curve lies within 1.96 standard errors (scipy.stats.norm.ppf(0.975)).
    p = k / n
    center = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return center - half, center + half


def miles_needed(rate, confidence=0.95):
    """Miles to drive with zero failures to show the failure rate is below `rate` per mile."""
    # NOTE: why -ln(1 - confidence): with zero failures in m miles, a true rate x gives zero failures
    #       with chance e^(-x*m) (Poisson); setting that to 5% gives m = -ln(0.05) / x = 3.0 / x,
    #       the "rule of three" (math.log is ln).
    #       Example: to show a failure rate below 1 in 1,000 miles, drive 3 / 0.001 = 3,000 miles with zero failures.
    #       Assumes: a constant failure rate (a Poisson process, so the gaps between failures are exponential),
    #       independent failures, and zero failures seen. With 1 or more failures, use the exact Poisson bound.
    return -math.log(1 - confidence) / rate
