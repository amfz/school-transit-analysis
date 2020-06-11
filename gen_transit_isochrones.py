import json
import os
import requests
import pandas as pd

school_list = 'outputs/geocoded_schools.csv'

# variables to run single process
school = '31.7704619,-106.4687935'
city = 'elpaso'
triptime = '3:30pm'
ampm = triptime[-2:]
file_name = 'outputs/{}/isos_{}_may12.geojson'.format(city, triptime.replace(':', ''))


def query_otp(coords, city, triptime, cutoffs=[30, 45, 60, 75, 90], 
              ampm='am', test_mode=True):
    """
    Makes a call to a running OpenTripPlanner instance for walking isochrones.
    
    Args:
        coords (str): Coordinate pair to generate isochrone from, in lat, lon format.
        city (str): Name of the city/router for OTP use. 
            Assumes an OTP instance is running locally with the given city name.
        triptime (str): Time to pass to API. Expected format examples: '7:30am', '4:00pm'.
            If arriveBy is not set, this will be the departure time.
        cutoffs (int or list of ints): Isochrone cutoff values in minutes.
            To generate isochrones for several time cutoffs, pass a list.
            Defaults to [30, 45, 60, 75, 90].
        ampm (str): Whether to query for AM or PM trips. 
            Accepted values: ('am', 'pm').
        test_mode (bool): Whether to call the function in test mode. 
            If True, the API will not be called. Parameters and endpoint URL will be returned instead.
            Defaults to True.

    Returns:
        json: JSON isochrone results.
        (if test_mode == True)
            str: fully-formed API URL.
            params: parameters passed to OpenTripPlanner.
    """
    api = 'http://localhost:8080/otp/routers/{}/isochrone'.format(city)
    header = {'Accept' : 'application/json'}
    cutoffs = [i * 60 for i in cutoffs]
    params = {
        'fromPlace': coords,
        'mode': 'WALK,TRANSIT',
        'date': '05-12-2020',
        'time': triptime,
        'cutoffSec': cutoffs,
        'clampInitialWait': 900,
        'maxTransfers': 1
    }
    if ampm == 'am':
        params['toPlace'] = coords
        params['arriveBy'] = True
    elif ampm == 'pm':
        params['arriveBy'] = False

    # debugging mode: return api endpoint and params    
    if test_mode:
        return api, params

    # request mode    
    r = requests.get(api, headers=header, params=params)
    if r.status_code == 200:
        return r.json()


def batch_process(city='houston'):
    """temporary home for houston batch code"""
    all_schools = pd.read_csv(school_list)
    # get only schools in the city that have session times
    all_schools = all_schools[all_schools['tz'].notnull()]
    city_schools = all_schools[all_schools['address'].str.contains(city, case=False)]

    for idx, row in city_schools.iterrows():
        # make a school-specific directory
        school_name = row['campus'].replace(' ', '_').lower()
        os.makedirs('outputs/{}/{}'.format(city, school_name), exist_ok=True)

        # get details for API call
        coordinates = '{lat},{lon}'.format(lat=row['school_lat'], 
                                           lon=row['school_lon'])
        am_time = row['am_latest_arr'].replace(' ', '').lower()
        pm_time = row['pm_earliest_dep'].replace(' ', '').lower()

        # adjust am time by 5 minutes
        #am_min = row['am_earliest_arr'][2:4]
        #am_replacement_min = str(int(am_min) + 10).rjust(2, '0')
        #am_time = am_time.replace(am_min, am_replacement_min)

        # format output paths
        am_out_file = '''outputs/{}/{}/isos_{}_may12_15minclamp.geojson'''.format(city, 
                                                                school_name, 
                                                                am_time.replace(':', ''))
        
        pm_out_file = '''outputs/{}/{}/isos_{}_may12_15minclamp.geojson'''.format(city, 
                                                                school_name, 
                                                                pm_time.replace(':', ''))
        
        # query and write am isochrones
        am = query_otp(coordinates, 
                       city=city, 
                       triptime=am_time, 
                       ampm='am',
                       test_mode=False)
        am['name'] = 'AM Isochrones'
        for f in am['features']:
            f['properties']['time'] = f['properties']['time']/60
        with open(am_out_file, 'w') as am_out:
            json.dump(am, am_out)

        # query and write pm isochrones
        pm = query_otp(coordinates, 
                       city=city, 
                       triptime=pm_time, 
                       ampm='pm',
                       test_mode=False)
        pm['name'] = 'PM Isochrones'
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
                    test_mode=False)

    with open(file_name, 'w') as out:
        json.dump(ans, out)
        print('Wrote file {}'.format(file_name))

batch_process()