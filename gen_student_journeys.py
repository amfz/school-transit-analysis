import configparser
import requests
import json
import time
import pandas as pd
import convert_times
from datetime import datetime

# variables
school = '000_school_name'
ampm = 'am'

# path templates
od_path = 'temp/indy/{}_od_df.csv'.format(school)
out_path = 'temp/indy/{}_{}_journeys.json'.format(school, ampm)

# API variables
dir_api = 'https://maps.googleapis.com/maps/api/directions/json'
config = configparser.ConfigParser()
config.read('config.ini')
gkey = config['auth']['gkey2']


def format_params(record, ampm):
    """
    Create the parameters to pass to the Google Directions API

    Args:
        record (pandas Series): a row of student data from an od_df dataset.
        ampm (str): whether the journey is 'am' or 'pm'
    
    Returns:
        dict: Dictionary of parameters needed for the Google Directions API
    """
    # basic parameters
    params = {'key': gkey,
              'mode': 'transit',
              'units': 'imperial'}

    if ampm=='am':
        # add origin, destination, arrival time for AM
        params['origin'] = '{}'.format(record['home_address'])
        params['destination'] = '{}'.format(record['school_address'])
        
        # format the arrival time to be school session time next Weds
        arr_text = record['am_latest_arr'] + ' ' + record['tz']
        arr_timestamp = convert_times.create_timestamp(arr_text)                                           
        params['arrival_time'] = arr_timestamp

    elif ampm=='pm':
        # add origin, destination, departure time for PM
        params['origin'] = '{}'.format(record['school_address'])
        params['destination'] = '{}'.format(record['home_address'])

        # format departure time to be school end bell next Weds
        dep_text = record['pm_earliest_dep'] + ' ' + record['tz']
        dep_timestamp = convert_times.create_timestamp(dep_text)
        params['departure_time'] = dep_timestamp

    return params


def query_dir_api(params):
    """
    Query the Google Directions API.

    Args:
        params (dict): Parameters to use in the API call.
    
    Returns:
        dict: JSON-formatted response, if successful.
              If the API call failed, dict will contain status code and params.
    """
    r = requests.get(dir_api, params=params)
    time.sleep(.05)
    if r.status_code == 200:
        data = r.json()
    else:
        data = {}
        data['status'] = r.status_code
        data['params'] = params
        print(r.status_code)
        time.sleep(60)
    return data


def batch_process(df, ampm):
    all_journeys = []
    for idx, row in df.iterrows():
        print(idx)
        params = format_params(row, ampm)
        response = query_dir_api(params)
        if response.get('status') != 'OK' and response.get('status') is not None:
            response['geocoded_waypoints'][0]['address'] = params['origin']
            response['geocoded_waypoints'][1]['address'] = params['destination']
        all_journeys.append(response)
    return all_journeys


def main():
    od = pd.read_csv(od_path)
    full_results = batch_process(od, ampm)

    with open(out_path, 'w') as out:
        json.dump(full_results, out)
        print('wrote to {}'.format(out_path))


if __name__ == '__main__':
    main()