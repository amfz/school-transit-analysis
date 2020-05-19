# School Transit Analysis

**NOTE: This is the public-facing version of a private repository. Files may be missing, and code may not be up-to-date with the private repo.**

## Requirements
### Software
#### OpenTripPlanner
* http://docs.opentripplanner.org/en/latest/: This project uses OTP v 1.4.0, available at https://repo1.maven.org/maven2/org/opentripplanner/otp/1.4.0/
* Resources
  * http://dev.opentripplanner.org/apidoc/1.0.0/resource_LIsochrone.html Documentation for OpenTripPlanner's isochrone API
  * [OpenTripPlanner - creating and querying your own multi-modal route planner](https://www.researchgate.net/publication/321110774_OpenTripPlanner_-_creating_and_querying_your_own_multi-modal_route_planner): Useful introduction to OpenTripPlanner and isochrone generation. Uses R but the methodology is applicable with other languages.

### Data Sources
* **ZCTAS** shapefiles from Census Bureau from https://www.census.gov/geographies/mapping-files/time-series/geo/carto-boundary-file.html
* **GTFS data** from https://transitfeeds.com/l/31-united-states
* **OSM extracts**
  * From https://www.interline.io/osm/extracts/ for Houston and the Twin Cities
  * Simple OSM extract from https://www.openstreetmap.org/export#map=10/39.8070/-86.1383 for Indianapolis
  * Overpass Turbo (https://overpass-turbo.eu/) for El Paso with the following query:
  ```
  area["name"="El Paso"]->.boundaryarea;
  (nwr(area.boundaryarea););
  out;
  ```
  

## Running
### Data Prep
1. Ensure addresses are clean enough to work with a geocoder (building number, street name, street type, and city name are present at minimum; preferably state and ZIP code are present as well). School addresses should be under the `Address` column in their csv. Student addresses should be consolidated in a column called `home_address`.
2. Time zones are specified in a `tz` column in the school list. Expected format is three letters, all caps, e.g. "EDT".

### Order the scripts should be run in
#### General Preprocessing
1. `geocode_schools.py` and (optionally) `geocode_students.py`: Geocoded schools are necessary for isochrones.

#### Generating Isochrones
1. `gen_transit_isochrones.py`

#### Generating Indiviual Student Journeys
1. `create_od_records.py`
2. `gen_student_journeys.py`
3. `postprocess_journeys.py`
