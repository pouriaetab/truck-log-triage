import contract
import pandas as pd
import pytest

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
