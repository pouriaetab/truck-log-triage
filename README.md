# truck-log-triage

Triage of autonomous truck drive logs, built one small step at a time: from the raw sensor log to a filed, tracked bug.
It runs on MAN TruckScenes, real data from a truck with 6 lidars, 6 radars and 4 cameras.

## Steps

0. Setup: Python 3.14 everywhere, every package locked with uv, and a check on every pull request (ruff and pytest).
1. scripts/get_metadata.sh, docsdata-dictionary.md and notebooks/01_eda.ipynb: download the metadata, describe every column of the 14 tablkes, answer nine questions about the data with SQL, and file bugs with the data's own table and sensor names.

## Step 1: what is in the data
`scripts/get_metadata.sh` downloads the metadata (14 MB). [The data dictionary](docs/data-dictionary.md) describes every column of the 14 tables (106 in all); [the notebook](notebooks/01_eda.ipynb) answers nine questions with SQL. What it found:

1. 10 scenes of 20 seconds, 400 key frames, each with all 16 sensor readings; cameras and lidars record about 10 times a second, radars about 20.
2. 25,750 labeled boxes on 1,094 tracked objects, most of them cars and traffic signs.
3. Lidar points per box drop from about 800 within 25 m to about 5 past 200 m; radar sees no box past 200 m.
4. The strongest "braking", -5.9 m/s^2, is vibration: the speed stays at 23.7 m/s. With a half-second average (a working choice from 10 scenes) the strongest real brake is -1.16 m/s^2, and the speed confirms it.
5. In two scenes the chassis speed sensor reads 0 for all 20 seconds while the truck drove about 6 m/s (its position and the cab sensor agree). Speed comes from the cab sensor or the position, never the chassis alone.

## Step 2: data contract

`scripts/contract.py` checks that the logs hang together before any finding is built on them, and CI runs it on the
real metadata on every pull request:

1. Every link points to a real row (9 links, e.g. every labeled box to a real key frame and tracked object).
2. Time only goes forward along every prev link.
3. Every key frame has all 16 sensor readings.
4. No gap longer than 0.05 s in the motion and position data, which record 100 times a second.
5. Speed from three sources (chassis sensor, cab sensor, GPS position) agrees within 0.5 m/s; a 2 of 3 vote names
   the broken source, and the scenes listed in `docs/known-data-issues.csv` are the only ones allowed to fail.

`scripts/kinematics.py` (distance and speed change) is checked with property based tests (hypothesis).

## Run the checks

```
uv sync --locked
uv run ruff check . && uv run ruff format --check . && uv run pytest -v
```

## Data and credit

MAN TruckScenes by MAN Truck & Bus, licensed CC BY-NC-SA 4.0 (non-commercial, with credit).
The data is never stored in this repo; each step's script downloads what it needs into data/.

## Limits of the data

MAN TruckScenes is a public research dataset, not a company fleet log. What it does not record, and what to keep in mind when reading any number here, is in [docs/data-limits.md](docs/data-limits.md), with a source for each line.
