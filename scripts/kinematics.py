"""kinematics.py: distance and speed change, the two small formulas every later step uses. (How something moved)"""

import math


def ground_distance(x1, y1, x2, y2):
    """Straight-line distance on the ground between two points, in meters (Pythagoras)"""
    return math.hypot(x2 - x1, y2 - y1)


def speed_change(v0, v1, dt):
    """Acceleration in m/s^2 from speed v0 to speed v1 over dt seconds; negative means braking."""
    if dt <= 0:
        raise ValueError("dt must be positive")
    return (v1 - v0) / dt
