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
