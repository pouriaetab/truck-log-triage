"""exposure.py: how often each kind of situation shows up in the data, with a 95% range and its E class."""

import json
from collections import Counter
from pathlib import Path

from safety_stats import e_class, wilson

SCENES = Path("data/man-truckscenes/v1.2-mini/scene.json")
TAGS = ["weather.rain", "weather.snow", "lighting.dark", "area.highway", "construction.roadworks"]


def tag_counts(scenes):
    """How many scenes carry each tag, e.g. weather.rain: 2. A scene counts once, not once per frame."""
    return Counter(tag for s in scenes for tag in s["description"].split(";"))


def main():
    scenes = json.loads(SCENES.read_text())
    n = len(scenes)
    counts = tag_counts(scenes)
    print(f"{n} scenes of {scenes[0]['nbr_samples']} key frames each")
    for tag in TAGS:
        k = counts[tag]
        lo, hi = wilson(k, n)
        print(
            f"{tag:24} {k}/{n} = {k / n:4.0%}   95% range {lo:4.0%} to {hi:4.0%}   E class {e_class(lo)} to {e_class(hi)}"
        )


if __name__ == "__main__":
    main()
