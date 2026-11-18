import math

import pytest
from hypothesis import given
from hypothesis import strategies as st
from kinematics import ground_distance, speed_change

coord = st.floats(min_value=-1e5, max_value=1e5, allow_nan=False)  # meters, about the size of a city map
# NOTE: speed is in m/s (1 m/s = 2.237 mph). The data comes from German trucks: their limit is 80 km/h (22 m/s,
#       50 mph), and the fastest in the mini data (10 scenes) is about 25 m/s (90 km/h, the speed limiter on EU
#       trucks); Step 2b re-checks it on all 598 scenes. The test range is twice that, so a US truck (75 mph =
#       34 m/s) or a bad reading is covered too.
speed = st.floats(min_value=-50, max_value=50, allow_nan=False)  # m/s
step = st.floats(min_value=0.01, max_value=10)  # seconds between two readings


def test_ground_distance_3_4_5():
    assert ground_distance(0, 0, 3, 4) == 5


@given(coord, coord, coord, coord)
def test_distance_is_never_negative_and_same_both_ways(x1, y1, x2, y2):
    d = ground_distance(x1, y1, x2, y2)
    assert d >= 0
    assert d == ground_distance(x2, y2, x1, y1)


@given(coord, coord, coord, coord, coord, coord)
def test_distance_triangle_rule(x1, y1, x2, y2, x3, y3):
    direct = ground_distance(x1, y1, x3, y3)
    via = ground_distance(x1, y1, x2, y2) + ground_distance(x2, y2, x3, y3)
    assert direct <= via + 1e-6  # 0.0000001 m of slack for computers dec rounding


@given(speed, speed, step)
def test_speed_change_gets_back_the_end_speed(v0, v1, dt):
    assert math.isclose(v0 + speed_change(v0, v1, dt) * dt, v1, abs_tol=1e-9)  # 0.000000001 for computers dec rounding


@given(speed, step)
def test_no_speed_change_means_zero(v, dt):
    assert speed_change(v, v, dt) == 0


def test_speed_change_refuses_zero_time():
    with pytest.raises(ValueError):
        speed_change(5, 6, 0)