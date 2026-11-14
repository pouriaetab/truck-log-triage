from exposure import tag_counts


def test_tag_counts_counts_scenes_not_frames():
    scenes = [
        {"description": "weather.rain;area.highway", "nbr_samples": 40},
        {"description": "weather.clear;area.highway", "nbr_samples": 40},
    ]
    counts = tag_counts(scenes)
    assert counts["weather.rain"] == 1 and counts["area.highway"] == 2
