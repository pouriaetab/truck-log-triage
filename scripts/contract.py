"""contract.py: checks that the logs hand together, before any finding is built on them."""

from pathlib import Path

import pandas as pd

DATA = Path(__file__).resolve().parent.parent / "data" / "man-truckscenes" / "v1.2-mini"


def load(name, data=DATA):
    """One table as a DataFrame, e.g. load("sample"), with timestamps as whole microseconds."""
    df = pd.read_json(data / f"{name}.json")
    if "timestamp" in df:
        df["timestamp"] = df["timestamp"].astype("int64")  # ego_pose writes some as 123.0
    return df


def orphans(child, key, parent):
    """Rows of child whose key is not a token in parent: a link that points nowhere."""
    return child[~child[key].isin(parent["token"])]


def backwards(df, time="timestamp"):
    """Rows that are not later than the row their prev link points to: time must go forward."""
    before = df[["token", time]].rename(columns={"token": "prev", time: "prev_time"})
    linked = df.merge(before, on="prev")  # a first row has prev '' and finds no partner
    return linked[linked[time] <= linked["prev_time"]]


def missing_readings(sample_data, sample, sensors=16):
    """Key frames with fewer key readings than there are sensors."""
    per_frame = sample_data[sample_data["is_key_frame"]].groupby("sample_token").size()
    per_frame = per_frame.reindex(sample["token"], fill_value=0)  # a frame with no reading at all counts as 0
    return per_frame[per_frame < sensors]


def motion_gaps(motion, sample, max_gap_s=0.05):
    """Gaps longer than max_gap is between motion readings, inside each scene's time window."""
    # NOTE: why 0.05 s: motion is recorded 100 times a second (0.01 s apart), so 0.05 s is 4 readings lost in a
    #       row; the largest normal gap in the mini data is 0.015 s, so jitter never trips it.
    windows = sample.groupby("scene_token")["timestamp"].agg(["min", "max"])
    found = []
    for scene, (t0, t1) in windows.iterrows():
        times = motion.loc[motion["timestamp"].between(t0, t1), "timestamp"].sort_values()
        gaps = times.diff() / 1e6  # microseconds to seconds
        for start, gap in zip(times.shift(), gaps):
            if gap > max_gap_s:
                found.append({"scene_token": scene, "start": int(start), "gap_s": round(gap, 3)})
    return pd.DataFrame(found, columns=["scene_token", "start", "gap_s"])
