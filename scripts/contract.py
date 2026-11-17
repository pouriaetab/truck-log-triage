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


def position_speed(frames):
    """Speed in m/s from GPS positions x, y: the distance from the key frame before to the one after, over that time."""
    # NOTE: why after minus before (a central difference), not diff(): diff() is this frame minus the one before,
    #       the average speed over the 0.5 s BEFORE the frame, so it runs late while the truck brakes (from 21 m/s
    #       at 4 m/s2: diff gives 20 at the frame, after minus before gives 19, the true speed). Against the cab
    #       sensor on the mini data: diff -0.21 to +0.24 m/s, central -0.12 to +0.17 (95% limits). diff() is right
    #       for gaps and for live use, where the next frame does not exist yet. The first and last key frame of a
    #       scene have no frame on one side, so they get NaN (no value).
    scene = frames.groupby("scene")
    dx = scene["x"].shift(-1) - scene["x"].shift(1)
    dy = scene["y"].shift(-1) - scene["y"].shift(1)
    dt = (scene["timestamp"].shift(-1) - scene["timestamp"].shift(1)) / 1e6
    return (dx**2 + dy**2) ** 0.5 / dt


def key_frame_speeds(sample, chassis, cabin, pose, scene):
    """Forward speed (m/s) at every key frame from three sources: chassis sensor, cab sensor, GPS position."""
    cols = ["token", "scene_token", "timestamp", "ego_motion_chassis_token", "ego_motion_cabin_token", "ego_pose_token"]
    out = sample[cols]
    out = out.merge(chassis[["token", "vx"]].rename(columns={"token": "ego_motion_chassis_token", "vx": "chassis"}))
    out = out.merge(cabin[["token", "vx"]].rename(columns={"token": "ego_motion_cabin_token", "vx": "cabin"}))
    out = out.merge(pose[["token", "translation"]].rename(columns={"token": "ego_pose_token"}))
    out = out.merge(scene[["token", "name"]].rename(columns={"token": "scene_token", "name": "scene"}))
    out = out.sort_values(["scene", "timestamp"]).reset_index(drop=True)
    out["x"], out["y"] = out["translation"].str[0], out["translation"].str[1]
    out["position"] = position_speed(out)
    return out[["token", "scene", "chassis", "cabin", "position"]]


def limits_of_agreement(a, b):
    """Bland-Altman: the mean difference a - b and the range that holds about 95% of the differences."""
    d = a - b
    mean, sd = float(d.mean()), float(d.std())
    return round(mean, 3), round(mean - 1.96 * sd, 3), round(mean + 1.96 * sd, 3)


def odd_source(speeds, tol=0.5):
    """Scenes where one speed source is more than tol m/s from the middle of the three: scene, source, largest gap."""
    # NOTE: why a vote: two sources only say that they disagree; with three, the middle value (median) sits with the
    #       two that agree, so the source far from it is the broken one.
    # NOTE: why 0.5 m/s: where all three work, every pair agrees within about 0.2 m/s (95% limits, Bland-Altman),
    #       so 0.5 is well above normal noise and far below a sensor stuck at zero (about 6 to 8 m/s off here).
    # NOTE: limit: GPS speed has no sign, so a truck reversing would show as a mismatch (none in the mini data).
    three = speeds.dropna(subset=["position"])  # two values cannot vote
    middle = three[["chassis", "cabin", "position"]].median(axis=1)
    found = []
    for source in ["chassis", "cabin", "position"]:
        gap = (three[source] - middle).abs()
        for scene, worst in gap[gap > tol].groupby(three["scene"]).max().items():
            found.append({"scene": scene, "source": source, "gap": round(worst, 2)})
    return pd.DataFrame(found, columns=["scene", "source", "gap"])
