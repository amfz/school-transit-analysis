import os
from osgeo import gdal, ogr
import geopandas as gpd


for subdir, dirs, files in os.walk('outputs\\indy'):
    for f in files:
        if 'isos' in f:
            # format output path
            geoj_path = os.path.join(subdir, f)
            new_file_name = f[8:10] + '_isochrones.kml'
            out_path = os.path.join(subdir, new_file_name)
            print(out_path)

            # sometimes isos are mappable but encoded oddly
            # this section below fixes that but is optional
            #isos = gpd.read_file(geoj_path)
            #isos['geometry'] = isos.buffer(0.00)
            #isos.to_file(geoj_path, driver='GeoJSON')

            # convert to kml
            geo_data = gdal.OpenEx(geoj_path)
            gdal.VectorTranslate(out_path, geo_data, format='kml')
        if '_journeys.geojson' in f:
            geoj_path = os.path.join(subdir, f)
            new_file_name = f[0:11] + '.kml'
            out_path = os.path.join(subdir, new_file_name)
            print(out_path)
            geo_data = gdal.OpenEx(geoj_path)
            gdal.VectorTranslate(out_path, geo_data, format='kml')
