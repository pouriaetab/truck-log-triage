from pathlib import Path

import contract
import pandas as pd
import pytest

KNOWN = Path(__file__).parent.parent / "docs" / "known-data-issues.csv"
needs_data = pytest.mark.skipif(not (contract.DATA / "scene.json").exists(), reason="run scripts/get_metadata.sh first")


def test_orphans_finds_a_link_to_nowhere():
    parent = pd.DataFrame({"token": ["a", "b"]})
    child = pd.DataFrame({"token": ["x", "y"], "parent_token": ["a", "zz"]})
    assert contract.orphans(child, "parent_token", parent)["token"].tolist() == ["y"]


@needs_data
def test_every_link_points_to_a_real_row():
    links = [
        ("sample", "scene_token", "scene"),
        ("sample", "ego_pose_token", "ego_pose"),
        ("sample_data", "sample_token", "sample"),
        ("sample_data", "calibrated_sensor_token", "calibrated_sensor"),
        ("calibrated_sensor", "sensor_token", "sensor"),
        ("sample_annotation", "sample_token", "sample"),
        ("sample_annotation", "instance_token", "instance"),
        ("sample_annotation", "visibility_token", "visibility"),
        ("instance", "category_token", "category"),
    ]
    for child, key, parent in links:
        assert contract.orphans(contract.load(child), key, contract.load(parent)).empty, f"{child}.{key} -> {parent}"


def test_backwards_finds_a_step_back_in_time():
    df = pd.DataFrame({"token": ["a", "b", "c"], "prev": ["", "a", "b"], "timestamp": [10, 20, 15]})
    assert contract.backwards(df)["token"].tolist() == ["c"]


@needs_data
def test_time_only_goes_forward():
    for name in ["sample", "sample_data", "ego_motion_chassis", "ego_motion_cabin"]:
        assert contract.backwards(contract.load(name)).empty, name


def test_missing_readings_counts_frames_without_all_sensors():
    sample = pd.DataFrame({"token": ["f1", "f2", "f3"]})
    sample_data = pd.DataFrame({"sample_token": ["f1", "f1", "f2"], "is_key_frame": [True, True, True]})
    assert contract.missing_readings(sample_data, sample, sensors=2).to_dict() == {"f2": 1, "f3": 0}


@needs_data
def test_every_key_frame_has_all_16_readings():
    assert contract.missing_readings(contract.load("sample_data"), contract.load("sample")).empty


def test_motion_gaps_find_a_hole():
    sample = pd.DataFrame({"scene_token": ["s", "s"], "timestamp": [0, 1_000_000]})
    motion = pd.DataFrame({"timestamp": [0, 10_000, 20_000, 120_000, 130_000]})  # 0.1 s missing after 0.02 s
    found = contract.motion_gaps(motion, sample)
    assert found.to_dict("records") == [{"scene_token": "s", "start": 20_000, "gap_s": 0.1}]


@needs_data
def test_no_motion_gaps():
    sample = contract.load("sample")
    for name in ["ego_motion_chassis", "ego_motion_cabin", "ego_pose"]:
        assert contract.motion_gaps(contract.load(name), sample).empty, name


def test_limits_of_agreement_on_known_numbers():
    a = pd.Series([1.1, 0.9, 1.1, 0.9])
    b = pd.Series([1.0, 1.0, 1.0, 1.0])
    assert contract.limits_of_agreement(a, b) == (0.0, -0.226, 0.226)


def test_position_speed_uses_the_frame_before_and_after():
    frames = pd.DataFrame({"scene": ["s"] * 3, "timestamp": [0, 500_000, 1_000_000], "x": [0, 3, 6], "y": [0, 4, 8]})
    speed = contract.position_speed(frames)
    assert speed.isna().tolist() == [True, False, True]  # the first and last frame have no neighbor on one side
    assert speed[1] == 10.0  # from (0, 0) to (6, 8) is 10 m, in 1 s


def test_odd_source_names_the_broken_sensor():
    speeds = pd.DataFrame(
        {
            "scene": ["ok", "stuck at zero", "edge"],
            "chassis": [5.0, 0.0, 0.0],
            "cabin": [5.02, 6.2, 9.0],
            "position": [5.05, 6.1, None],
        }
    )
    assert contract.odd_source(speeds).to_dict("records") == [
        {"scene": "stuck at zero", "source": "chassis", "gap": 6.1}
    ]


@needs_data
def test_speed_sources_agree_except_known_issues():
    sample, scene, pose = contract.load("sample"), contract.load("scene"), contract.load("ego_pose")
    chassis, cabin = contract.load("ego_motion_chassis"), contract.load("ego_motion_cabin")
    speeds = contract.key_frame_speeds(sample, chassis, cabin, pose, scene)
    known = pd.read_csv(KNOWN).query("check == 'speed_mismatch'")
    found = contract.odd_source(speeds)
    assert set(zip(found["scene"], found["source"])) == set(zip(known["scene"], known["source"]))
