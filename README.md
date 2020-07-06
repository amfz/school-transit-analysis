# School Transit Analysis

**NOTE: This is the public-facing version of a private repository. Files are missing, and code may not be up-to-date with the private repo.**

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
   * Alternatively, consider using `osmnx` 
 
## Running
### Build OpenTripPlanner graphs
1. Collect OSM and GTFS data in the same folder. OTP expects a specific folder structure: `otp/graphs/[desiredroutername]`. See the OpenTripPlanner tutorial and docs above for details.
2. In the command line, navigate to your `otp` folder and run the following command, replacing bracketed values:  
`java -Xmx4096m -jar [otp.jar file] --build graphs/[routername]`


### Data Prep
1. Ensure addresses are clean enough to work with a geocoder (building number, street name, street type, and city name are present at minimum; preferably state and ZIP code are present as well). School addresses should be under a single school address column in their csv. Student addresses should be consolidated into a single column as well.
2. Time zones should be specified in a `tz` column in the school list. Expected format is three letters, all caps, e.g. "EDT".
3. School bell times will need to be in columns called `am_latest_arr` and `pm_earliest_dep` when run through `gen_student_journeys`

### Order the scripts should be run in
#### General Preprocessing
1. `geocode_and_prep.py`: Geocoded schools are necessary for isochrones. This script also cleans input data and makes sure the needed column names exist for `create_od_records.py`

#### Generating Isochrones
1. `start_otp.py`: optional script to start OTP.
  a. Alternatively, navigate in the command line to your `/otp` directory an run the following command there:  
    `java -Xmx4096m -jar otp-1.4.0-shaded.jar --router [routername] --graphs graphs --server`
2. `gen_transit_isochrones.py`

#### Generating Indiviual Student Journeys
1. `create_od_records.py`: Merge student and school data so each row contains information on student location, school location, bell times, and time zone
2. `gen_student_journeys.py`: run journeys through the Google Directions API
3. `postprocess_journeys.py`: extract journey metrics (and optional shapes) from the Directions API results
4. `convert_geojson_to_kml.py`: optional, if postprocessing created geoJSONs, convert them to KMLs for Google Maps
