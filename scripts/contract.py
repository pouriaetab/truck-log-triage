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
