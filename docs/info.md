#### Required manual data prep
1. Ensure addresses are clean enough to work with a geocoder (building number, street name, street type, and city name are present at minimum; preferably state and ZIP code are present as well). School addresses should be under the `Address` column in their csv. Student addresses should be consolidated in a column called `home_address`.
2. Time zones are specified in a `tz` column in the school list. Expected format is three letters, all caps, e.g. "EDT".

#### Order the scripts should be run in
##### General Preprocessing
1. `geocode_schools.py` and (optionally) `geocode_students.py`: Geocoded schools are necessary for isochrones.

##### Generating Isochrones
1. `gen_transit_isochrones.py`

##### Generating Indiviual Student Journeys
1. `create_od_records.py`
2. `gen_student_journeys.py`
3. `postprocess_journeys.py`
