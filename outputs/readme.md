# Outputs folder

This folder contains end-product data.

- Individual school folders containing AM and PM transit isochrones output by `gen_transit_isochrones.py`
  - If `geojson_to_kml.py` was run, both geoJSON and KML formatted files will be available. Otherwise, only geoJSON files will be available. 
- `[school_name]_am_journeys.geojson` and `[school_name]_pm_journeys.geojson`: Outputs of `postprocess_journeys.py`. GeoJSON-formatted line geometries for student journeys. Each feature also includes trip summary metrics.
  - KML files with the same naming convention will also appear here if `geojson_to_kml.py` was run
- `[school_name]_am_journey_attributes.csv` and `[school_name]_am_journey_attributes.csv`: Outputs of `postprocess_journeys.py`. CSV-formatted files containing trip summary statistics.
