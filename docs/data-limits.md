# Limits of the data

This repo uses MAN TruckScenes, a public research dataset (Fent et al., NeurIPS 2024; arXiv 2407.07462 version 2,
November 2024). It is not a company fleet log. Each row says what is missing or limited, why it matters for the work
here, and where it comes from. The list is not complete.

Data used so far: the mini release (10 scenes), metadata only, no lidar, radar or camera files.

## How the scenes were chosen

| # | Limit | Why it matters here | Source |
|---|---|---|---|
| 1 | The 747 scenes were picked by hand from more than 25 hours of drives, to be diverse and challenging. | Shares in the data (rain, night, terminal) describe the picked scenes, not real driving time, so exposure (E) from the data is a guide, not a rate. | paper, section 3.5 |
| 2 | How the 10 mini scenes were picked is not stated. Mini has 4 city scenes of 10, while the paper says the release is mostly highway, terminal and rural, and it holds one each of snow, dark and roadworks: it looks picked for variety. | A share from mini can be far from the full release. | paper and devkit (not stated); paper, appendix A.4 |
| 3 | Each scene is about 20 seconds; mini is 195 seconds in total. | No long events, no full trips, no before and after of a rare event. | paper, section 3.5 |
| 4 | One truck, Germany only, public roads and logistics terminals, long-haul use. | Results may not hold for other trucks, countries, road rules or kinds of hauling. | paper, section 7 |
| 5 | The paper does not say whether a person or the automation was driving. | Braking and following may show a human driver's behavior, not a self-driving system's. | paper (not stated) |

## What is not recorded

| # | Limit | Why it matters here | Source |
|---|---|---|---|
| 6 | No vehicle bus (CAN) data: no wheel speed, transmission speed, steering angle, brake pressure, throttle or gear. | Speed comes only from the two motion sensors and GPS positions; a real truck has more sources to cross-check. | devkit issues #7 (Dec 2024) and #30 (Jan 2026) |
| 7 | No HD map. | Lanes, speed limits and road layout are not available, only GPS positions. | paper, Table 1; devkit issue #30 |
| 8 | No outputs of a self-driving system: no detections, tracks, planned paths, control commands, fault codes or takeovers. | Triage here starts from sensor data and labels, not from the system's own logs and alerts. | paper and schema (none listed) |
| 9 | Timestamps are shifted for privacy. | The real date and clock time are unknown; the scene tags give the time of day. | paper, section 3.8 |
| 10 | The height (z) in ego_pose is always 0. | Road slope must come from the motion sensors' pitch, not from position. | devkit schema |
| 11 | Faces and license plates are blurred. | No effect on these checks; noted for camera work. | paper, section 3.8 |

## How the sensors measure

| # | Limit | Why it matters here | Source |
|---|---|---|---|
| 12 | The motion sensors (IMUs) pick up vibration. | One acceleration reading can look like hard braking (-5.88 m/s2 while speed stayed at 23.6 m/s), so this repo averages over 0.5 s and checks the speed. | paper, section 7; Step 1 question 8 |
| 13 | The cab moves on its own suspension, apart from the chassis. | Cab sensor readings include cab motion; the chassis sensor is the one meant for truck motion. | paper, section 3.1; devkit issue #30 |
| 14 | The chassis speed reads 0 in 2 mini scenes while the truck is moving. | Speed from the chassis alone would call a moving truck stopped, so the cab sensor and GPS positions check it. | Step 1 question 9; Step 2 ship 5 |
| 15 | GPS positions have small errors even with RTK correction. | Distances and speeds worked out from positions carry that error. | paper, section 7 |
| 16 | Radars drop frames (about 19.6 per second instead of 20), and the number of readings between key frames varies by sensor. | Checks on readings between key frames must allow for it. | paper, section 3.4; devkit issue #26 |
| 17 | Boxes are drawn by people, 2 times a second; human errors are possible. | Label checks and any model trained on the labels inherit the errors. | paper, sections 3.6 and 7 |
| 18 | The trailer blocks the view behind the truck. | Fewer boxes behind the truck; a car close behind can be missed. | paper, section 3.1 |

## Size of the mini release

| # | Limit | Why it matters here | Source |
|---|---|---|---|
| 19 | 10 scenes, 400 key frames. | Shares have wide 95% ranges (rain is 2 of 10 scenes: 6% to 51%). | Step 1b |
| 20 | Rare things barely appear: 1 animal, and no tag marks a crash or near miss. | Rare hazards can be named (HARA, from the ODD) but not measured here. | Step 1 question 6; paper, section 3.6 |