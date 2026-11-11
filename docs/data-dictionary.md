# Data dictionary: MAN TruckScenes mini (v1.2)

Every column of the 14 tables, studied before any step is built. Counts are from the mini release.
Tables point to each other by token (an id). Times are microseconds since 1970. An empty link is `''` (empty text), not NULL.

## scene (10 rows): one 20-second drive

| Column | Type | Filled | Meaning | In the data |
|---|---|---|---|---|
| `name` | text | 10 of 10 | scene-<id> |  |
| `description` | text | 10 of 10 | 7 tags joined by ';': weather, area, daytime, season, lighting, structure, construction | split on ';' then on the first '.' (weather.rain -> weather: rain) |
| `token` | text | 10 of 10 | the scene's id |  |
| `log_token` | text | 0 of 10 | the recording log it came from | empty in all 10 rows: not usable |
| `nbr_samples` | integer | 10 of 10 | key frames in the scene | 40 in every scene (2 a second for 20 s) |
| `first_sample_token` | text | 10 of 10 | its first key frame |  |
| `last_sample_token` | text | 10 of 10 | its last key frame |  |
| `weather_annotation_token` | text | 10 of 10 | its weather row |  |

## sample (400 rows): one key frame: a moment, twice a second, when every sensor has a reading and the objects are labeled

| Column | Type | Filled | Meaning | In the data |
|---|---|---|---|---|
| `token` | text | 400 of 400 | the key frame's id |  |
| `scene_token` | text | 400 of 400 | its scene | 40 per scene |
| `timestamp` | integer | 400 of 400 | when, in microseconds since 1970 | divide by 1e6 for seconds |
| `prev` | text | 390 of 400 | the key frame before | '' (empty text, not NULL) for the first of each scene: 10 |
| `next` | text | 390 of 400 | the key frame after | '' for the last of each scene: 10 |
| `ego_motion_cabin_token` | text | 400 of 400 | the cab motion reading at this moment |  |
| `ego_motion_chassis_token` | text | 400 of 400 | the chassis motion reading at this moment |  |
| `ego_pose_token` | text | 400 of 400 | where the truck was at this moment |  |

## sample_data (43,556 rows): one reading of one sensor: a camera image or a lidar or radar point cloud

| Column | Type | Filled | Meaning | In the data |
|---|---|---|---|---|
| `token` | text | 43,556 of 43,556 | the reading's id |  |
| `sample_token` | text | 43,556 of 43,556 | the key frame it belongs to (or the nearest one for an in-between reading) |  |
| `ego_pose_token` | text | 43,556 of 43,556 | where the truck was when it was taken |  |
| `calibrated_sensor_token` | text | 43,556 of 43,556 | which mounted sensor took it | 16 distinct: the 2 IMUs have no readings here |
| `timestamp` | integer | 43,556 of 43,556 | when, in microseconds |  |
| `fileformat` | text | 43,556 of 43,556 | jpg (camera) or pcd (lidar or radar point cloud) | jpg 8,046 · pcd 35,510 |
| `is_key_frame` | true/false | 43,556 of 43,556 | true for the 16 readings of a key frame, false for the readings in between | true 6,400 (= 400 key frames × 16) · false 37,156 |
| `height` | integer | 43,556 of 43,556 | image height in pixels; 1 for a point cloud | jpg always 943 |
| `width` | integer | 43,556 of 43,556 | image width in pixels; for a point cloud, the number of points | jpg always 1,980; pcd 71 to 84,751 points |
| `filename` | text | 43,556 of 43,556 | the file in the sensor download: samples/ for key frames, sweeps/ for the rest | needed in step 4 (evidence views) |
| `prev` | text | 43,396 of 43,556 | the same sensor's reading before | '' for the first reading of each sensor in each scene: 160 |
| `next` | text | 43,396 of 43,556 | the same sensor's reading after | '' for the last: 160 |
| `ego_motion_cabin_token` | text | 43,556 of 43,556 | the cab motion reading closest in time |  |
| `ego_motion_chassis_token` | text | 43,556 of 43,556 | the chassis motion reading closest in time |  |

## sensor (18 rows): one of the 18 sensors

| Column | Type | Filled | Meaning | In the data |
|---|---|---|---|---|
| `token` | text | 18 of 18 | the sensor's id |  |
| `channel` | text | 18 of 18 | its name and place, such as LIDAR_LEFT or RADAR_RIGHT_BACK | XSENSE_CABIN and XSENSE_CHASSIS are the 2 IMUs |
| `modality` | text | 18 of 18 | lidar, radar, camera or imu | lidar 6 · radar 6 · camera 4 · imu 2 |

## calibrated_sensor (18 rows): where one sensor sits on the truck and how it points

| Column | Type | Filled | Meaning | In the data |
|---|---|---|---|---|
| `token` | text | 18 of 18 | the id |  |
| `sensor_token` | text | 18 of 18 | which sensor |  |
| `translation` | list | 18 of 18 | x, y, z in meters from the truck's reference point (x forward, y left, z up) |  |
| `rotation` | list | 18 of 18 | which way it points, as a quaternion (w, x, y, z: four numbers for a 3D rotation) |  |
| `camera_intrinsic` | list | 4 of 18 | the camera's 3×3 lens matrix (focal length and image center) | filled for the 4 cameras, an empty list for the other 14 |

## ego_pose (20,116 rows): where the truck was, and which way it faced, at one moment

| Column | Type | Filled | Meaning | In the data |
|---|---|---|---|---|
| `token` | text | 20,116 of 20,116 | the id |  |
| `timestamp` | integer | 20,116 of 20,116 | when, in microseconds | 4,025 of 20,116 values are written as decimals (…815.0), so DuckDB reads the column as DOUBLE; cast to BIGINT before joining on time |
| `translation` | list | 20,116 of 20,116 | x, y, z in meters in the map frame (UTM: x east, y north) | the truck's real path: speed = distance / time |
| `rotation` | list | 20,116 of 20,116 | heading as a quaternion |  |

## ego_motion_chassis (20,089 rows): the truck's motion from the IMU on the chassis, about 100 times a second

| Column | Type | Filled | Meaning | In the data |
|---|---|---|---|---|
| `token` | text | 20,089 of 20,089 | the id |  |
| `timestamp` | integer | 20,089 of 20,089 | when, in microseconds |  |
| `vx` | decimal | 20,089 of 20,089 | forward speed, m/s | reads 0.00 for the whole scene in 2 scenes where the truck moved (bridge 5.9 m/s, highway rain 6.8 m/s by its position): do not trust it alone |
| `vy` | decimal | 20,089 of 20,089 | sideways speed, m/s |  |
| `vz` | decimal | 20,089 of 20,089 | up/down speed, m/s |  |
| `ax` | decimal | 20,089 of 20,089 | forward acceleration, m/s² | −5.88 to +5.34; the −5.88 is vibration (speed did not drop) |
| `ay` | decimal | 20,089 of 20,089 | sideways acceleration, m/s² |  |
| `az` | decimal | 20,089 of 20,089 | up/down acceleration, m/s², gravity included (about 9.8) | 2.0 to 16.0: big bumps |
| `yaw` | decimal | 20,089 of 20,089 | heading angle, radians | drifts from 0.84 to 1.33 in the bridge scene while the truck's real heading stays flat |
| `pitch` | decimal | 20,089 of 20,089 | nose up/down angle, radians |  |
| `roll` | decimal | 20,089 of 20,089 | lean left/right angle, radians |  |
| `yaw_rate` | decimal | 20,089 of 20,089 | turning speed, radians per second |  |
| `pitch_rate` | decimal | 20,089 of 20,089 | pitch speed, rad/s |  |
| `roll_rate` | decimal | 20,089 of 20,089 | roll speed, rad/s |  |
| `prev` | text | 20,079 of 20,089 | the reading before | '' for the first of each scene: 10 |
| `next` | text | 20,079 of 20,089 | the reading after | '' for the last: 10 |

## ego_motion_cabin (20,090 rows): the same motion measured by the IMU in the cab (the cab rides on its own suspension)

| Column | Type | Filled | Meaning | In the data |
|---|---|---|---|---|
| `token` | text | 20,090 of 20,090 | the id |  |
| `timestamp` | integer | 20,090 of 20,090 | when, in microseconds |  |
| `vx` | decimal | 20,090 of 20,090 | forward speed, m/s | agrees with the truck's position in all 10 scenes (within 0.2 m/s on average) |
| `vy` | decimal | 20,090 of 20,090 | sideways speed, m/s |  |
| `vz` | decimal | 20,090 of 20,090 | up/down speed, m/s |  |
| `ax` | decimal | 20,090 of 20,090 | forward acceleration, m/s² | −2.51 to +2.82: smoother than the chassis |
| `ay` | decimal | 20,090 of 20,090 | sideways acceleration, m/s² |  |
| `az` | decimal | 20,090 of 20,090 | up/down acceleration with gravity, m/s² | 7.3 to 11.8 |
| `yaw` | decimal | 20,090 of 20,090 | heading angle, radians |  |
| `pitch` | decimal | 20,090 of 20,090 | pitch angle, radians |  |
| `roll` | decimal | 20,090 of 20,090 | roll angle, radians |  |
| `yaw_rate` | decimal | 20,090 of 20,090 | turning speed, rad/s |  |
| `pitch_rate` | decimal | 20,090 of 20,090 | pitch speed, rad/s |  |
| `roll_rate` | decimal | 20,090 of 20,090 | roll speed, rad/s |  |
| `prev` | text | 20,080 of 20,090 | the reading before | '' for the first of each scene: 10 |
| `next` | text | 20,080 of 20,090 | the reading after | '' for the last: 10 |

## sample_annotation (25,750 rows): one labeled 3D box around one object at one key frame

| Column | Type | Filled | Meaning | In the data |
|---|---|---|---|---|
| `token` | text | 25,750 of 25,750 | the box's id |  |
| `sample_token` | text | 25,750 of 25,750 | its key frame | up to 125 boxes in one key frame |
| `instance_token` | text | 25,750 of 25,750 | the tracked object it belongs to |  |
| `visibility_token` | text | 25,750 of 25,750 | how much of it the cameras see (level 1 to 4) | level 1: 8,346 · 2: 2,176 · 3: 2,034 · 4: 13,194 |
| `attribute_tokens` | list | 24,612 of 25,750 | a list of states (moving, parked, standing ...) | empty for 1,138 boxes: cones 857, trains 200, barriers 42, strollers 39; never more than one |
| `translation` | list | 25,750 of 25,750 | the box center x, y, z in the map frame, meters | distance to the truck = this minus the truck's ego_pose |
| `size` | list | 25,750 of 25,750 | width, length, height in meters | from 0.12 m to 58.9 m long |
| `rotation` | list | 25,750 of 25,750 | the box's heading as a quaternion |  |
| `prev` | text | 24,656 of 25,750 | the same object's box at the key frame before | '' for each object's first box: 1,094 |
| `next` | text | 24,656 of 25,750 | the same object's box at the key frame after | '' for its last box: 1,094 |
| `num_lidar_pts` | integer | 25,750 of 25,750 | lidar points inside the box | 1 to 50,999; never 0 |
| `num_radar_pts` | integer | 25,750 of 25,750 | radar points inside the box | 0 to 92; 0 in 13,690 boxes (53%) |

## instance (1,094 rows): one tracked object across its scene

| Column | Type | Filled | Meaning | In the data |
|---|---|---|---|---|
| `token` | text | 1,094 of 1,094 | the object's id |  |
| `category_token` | text | 1,094 of 1,094 | its class | 18 of the 27 classes appear |
| `nbr_annotations` | integer | 1,094 of 1,094 | how many boxes it has | 1 to 40 |
| `first_annotation_token` | text | 1,094 of 1,094 | its first box |  |
| `last_annotation_token` | text | 1,094 of 1,094 | its last box |  |

## category (27 rows): an object class

| Column | Type | Filled | Meaning | In the data |
|---|---|---|---|---|
| `token` | text | 27 of 27 | the id |  |
| `name` | text | 27 of 27 | the class, such as vehicle.car or human.pedestrian.adult | vehicle.ego_trailer is the truck's own trailer, not a road user |
| `description` | text | 27 of 27 | what the class covers, in words |  |
| `index` | integer | 27 of 27 | a number for the class, 1 to 27 |  |

## attribute (11 rows): a state an object can be in

| Column | Type | Filled | Meaning | In the data |
|---|---|---|---|---|
| `token` | text | 11 of 11 | the id |  |
| `name` | text | 11 of 11 | such as vehicle.moving, vehicle.parked, pedestrian.standing, cycle.with_rider | 11 states |
| `description` | text | 11 of 11 | what the state means, in words |  |

## visibility (4 rows): how much of an object the cameras see

| Column | Type | Filled | Meaning | In the data |
|---|---|---|---|---|
| `token` | text | 4 of 4 | the id |  |
| `level` | integer | 4 of 4 | 1 to 4 | 1: 0-40% · 2: 41-60% · 3: 61-80% · 4: 81-100% |
| `description` | text | 4 of 4 | the range in words |  |

## weather_annotation (10 rows): the weather for one scene

| Column | Type | Filled | Meaning | In the data |
|---|---|---|---|---|
| `token` | text | 10 of 10 | the id |  |
| `wind_speed` | decimal | 10 of 10 | wind, m/s | 0.1 to 4.8 |
| `wind_direction` | decimal | 10 of 10 | where the wind comes from, degrees | 177 to 358 |
| `precipitation` | decimal | 10 of 10 | rain or snow, mm per hour | 0 in 7 scenes; 4.27 the most |
| `temperature` | decimal | 10 of 10 | air temperature in kelvin (subtract 273.15 for °C) | 273.6 to 295.5 K = 0.5 to 22.4 °C |

## What to watch for in the next steps

1. Speed: use the cab's `vx` or the speed from `ego_pose`; the chassis `vx` reads 0 in two scenes where the truck moved.
2. Braking: look at the change in speed over half a second, not one `ax` reading (vibration reaches −5.9 m/s²).
3. Time: cast `ego_pose.timestamp` to BIGINT before joining on time.
4. Empty links are `''`, so `IS NULL` finds nothing: test `= ''`.
5. Boxes with no attribute are classes that have none (cones, trains, barriers) plus 39 strollers.