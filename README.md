# truck-log-triage

Triage of autonomous truck drive logs, built one small step at a time: from the raw sensor log to a filed, tracked bug.
It runs on MAN TruckScenes, real data from a truck with 6 lidars, 6 radars and 4 cameras.

## Steps

0. Setup: Python 3.14 everywhere, exact tool versions, and a check on every pull request (ruff and pytest).

## Run the checks

```
python3 -m pip install -r requirements.txt
ruff check . && python3 -m pytest -v
```

## Data and credit

MAN TruckScenes by MAN Truck & Bus, licensed CC BY-NC_SA 4.0 (non-commercial, with credit).
The data is never stored in this repo; each step's script downloads what it needs into data/.