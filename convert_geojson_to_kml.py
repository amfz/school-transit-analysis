import os
from osgeo import gdal, ogr

#geoj_path = 'outputs/elpaso/otp_isochrones_330pm_may12_clampwait.geojson'
#print(os.path.split(geoj_path))

for subdir, dirs, files in os.walk('outputs\\houston'):
    for f in files:
        #if '15min' in f:
        #    geoj_path = os.path.join(subdir, f)
        #    new_file_name = f[8:10] + '_isochrones.kml'
        #    out_path = os.path.join(subdir, new_file_name)
        #    print(out_path)
        #    geo_data = gdal.OpenEx(geoj_path)
        #    gdal.VectorTranslate(out_path, geo_data, format='kml')
        if '_journeys2.geojson' in f:
            geoj_path = os.path.join(subdir, f)
            new_file_name = f[0:11] + '.kml'
            out_path = os.path.join(subdir, new_file_name)
            print(out_path)
            geo_data = gdal.OpenEx(geoj_path)
            gdal.VectorTranslate(out_path, geo_data, format='kml')