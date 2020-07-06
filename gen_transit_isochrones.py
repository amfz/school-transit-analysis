import json
import os
import requests
import pandas as pd

# MODIFY THESE FOR BATCH PROCESSING
school_list = 'outputs/geocoded_indy_schools.csv'
router = 'indy2'

# variables to run single process
school = '31.7704619,-106.4687935'
city = 'elpaso'
triptime = '7:30am'
ampm = triptime[-2:]
file_name = 'outputs/{}/isos_{}.geojson'.format(city, triptime.replace(':', ''))


def query_otp(coords, city, triptime, cutoffs=[30, 45, 60, 75, 90], 
              maxwalkdist=None, ampm='am', test_mode=True):
    """
    Makes a call to a running OpenTripPlanner instance for transit isochrones.
    More parameters are available than are included here. 
    See http://dev.opentripplanner.org/apidoc/1.4.0/resource_LIsochrone.html for all options.
    
    Args:
        coords (str): Coordinate pair to generate isochrone from, in lat, lon format.
        city (str): Name of the city/router for OTP use. 
            Assumes an OTP instance is running locally on port 8080 (the OTP default) with the given city name.
        triptime (str): Time to pass to API. Expected format examples: '7:30am', '4:00pm'.
            For PM trips this value will be used as the departure time.
            For AM trips this value will be used as the arrive by time.
        cutoffs (int or list of ints): Isochrone cutoff values in minutes.
            To generate isochrones for several time cutoffs, pass a list.
            Defaults to [30, 45, 60, 75, 90].
        maxwalkdist (float): Maximum allowable walking distance, in miles. 
            Defaults to None -- no limit on walk distance will be imposed.
        ampm (str): Whether to query for AM or PM trips. 
            Accepted values: ('am', 'pm').
        test_mode (bool): Whether to call the function in test mode. 
            If True, the API will not be called. Parameters and endpoint URL will be returned instead.
            Defaults to True.

    Returns:
        (if test_mode == False)
            json: JSON isochrone results.
        (if test_mode == True)
            str: fully-formed API URL.
            params: parameters passed to OpenTripPlanner.
    """
    api = 'http://localhost:8080/otp/routers/{}/isochrone'.format(city)
    header = {'Accept' : 'application/json'}
    cutoffs = [i * 60 for i in cutoffs]

    # PARAMETERS TO PASS TO OTP
    params = {
        'fromPlace': coords,
        'mode': 'WALK,TRANSIT',
        'date': '06-17-2020',
        'time': triptime,
        'cutoffSec': cutoffs,
        'clampInitialWait': 900,
        'maxTransfers': 1
    }

    if maxwalkdist:
        # convert miles to meters for OTP
        params['maxWalkDistance'] = maxwalkdist * 1609.34

    # add additional parameters for AM trips
    if ampm == 'am':
        params['toPlace'] = coords
        params['arriveBy'] = True
        # Indianapolis uses different AM and PM acceptable arrival intervals
        params['clampInitialWait'] = 1200

    # add additional parameters for PM trips
    elif ampm == 'pm':
        params['arriveBy'] = False

    # debugging mode: return api endpoint and params    
    if test_mode:
        print(api)
        print(params)
        return api, params

    # request mode    
    r = requests.get(api, headers=header, params=params)
    if r.status_code == 200:
        return r.json()


def batch_process(locations, city='indy2'):
    """
    Process several school locations using the same OpenTripPlanner router.
    Function will create an AM isochrone and PM isochrone file for each school.
    Files will be saved
    
    Args:
        locations (str): path to csv for locations to use.
            Function will process all records with an am_latest_arr time.
            Assumes the locations file has the following fields:
              am_latest_arr
              pm_earliest_dep
              school_lat
              school_lon
              campus: school name
        city (str): name of the OpenTripPlanner router to use.

    Returns:
        None
    
    """
    all_schools = pd.read_csv(locations)
    # get only schools that have session times
    all_schools = all_schools[all_schools['am_latest_arr'].notnull()]

    for idx, row in all_schools.iterrows():
        # make a school-specific directory
        school_name = row['school_name'].replace(' ', '_')\
                                        .replace('@', 'at')\
                                        .replace('.', '')\
                                        .replace('/', '_')\
                                        .replace('\\', '_')\
                                        .lower()
        os.makedirs('outputs/{}/{}'.format(city, school_name), exist_ok=True)

        # get details for API call
        coordinates = '{lat},{lon}'.format(lat=row['school_lat'], 
                                           lon=row['school_lon'])
        am_time = row['am_latest_arr'].replace(' ', '').lower()
        pm_time = row['pm_earliest_dep'].replace(' ', '').lower()

        # format output paths
        am_out_file = '''outputs/{}/{}/isos_{}_jun17.geojson'''.format(city, 
                                                                school_name, 
                                                                am_time.replace(':', ''))
        
        pm_out_file = '''outputs/{}/{}/isos_{}_jun17.geojson'''.format(city, 
                                                                school_name, 
                                                                pm_time.replace(':', ''))
        
        # query and write am isochrones
        am = query_otp(coordinates, 
                       city=city, 
                       triptime=am_time, 
                       ampm='am',
                       maxwalkdist=1.5,
                       test_mode=False)
        am['name'] = '{}_am_isochrones'.format(school_name)
        for f in am['features']:
            f['properties']['time'] = f['properties']['time']/60
        with open(am_out_file, 'w') as am_out:
            json.dump(am, am_out)

        # query and write pm isochrones
        pm = query_otp(coordinates, 
                       city=city, 
                       triptime=pm_time, 
                       ampm='pm',
                       maxwalkdist=1.5,
                       test_mode=False)
        pm['name'] = '{}_pm_isochrones'.format(school_name)
        for f in pm['features']:
            f['properties']['time'] = f['properties']['time']/60
        with open(pm_out_file, 'w') as pm_out:
            json.dump(pm, pm_out)

        print('Made isochrones for {}'.format(school_name))


def single_process():
    ans = query_otp(school, 
                    city=city,
                    triptime=triptime, 
                    cutoffs=[30, 45, 60, 75, 90],
                    ampm=ampm,
                    maxwalkdist=2,
                    test_mode=False)

    with open(file_name, 'w') as out:
        json.dump(ans, out)
        print('Wrote file {}'.format(file_name))


batch_process(school_list, router)
#single_process()