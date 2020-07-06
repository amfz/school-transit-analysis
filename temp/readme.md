# Temp folder

This folder contains intermediate datasets. The files here are useful for auditing/error tracing, but are not meant to be provided to an end user.

File naming conventions:
- `[school_name]_geocoded_students.csv`: output of `geocode_and_prep.py`
- `[school_name]_od_df.csv`: output of `create_od_records.py`. This file takes a geocoded_students file and merges in school data so that each row contains a home location `home_address`), school location (`school_address`), AM bell time (`am_earliest_arr`), PM bell time (`pm_latest_dep`), and time zone (`tz`)
- `[school_name]_am_journeys.json`: output of `gen_student_journeys.py`. Google Directions API responses for individual students' AM journeys. Still needs postprocessing to get summary information/be mappable.
- `[school_name]_pm_journeys.json`: output of `gen_student_journeys.py`. Google Directions API responses for individual students' PM journeys. Still needs postprocessing to get summary information/be mappable.
