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
  
  ### Visualizations
  * **Heat Maps** guide to displaying point vector data as heat map from https://www.qgistutorials.com/en/docs/3/creating_heatmaps.html
 
