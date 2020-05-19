import configparser
import requests
import json
import time
import pandas as pd
import convert_times
from datetime import datetime

# file variables
od_path = 'inputs/elpaso/od_df.csv'
am_out_path = 'inputs/elpaso/am_journeys.json'
pm_out_path = 'inputs/elpaso/pm_journeys.json'

# API variables
dir_api = 'https://maps.googleapis.com/maps/api/directions/json'
config = configparser.ConfigParser()
config.read('config.ini')
gkey = config['auth']['gkey']

# setup
od = pd.read_csv(od_path)
sample = od.head(2)


def format_params(record, ampm):
    # basic parameters
    params = {'key': gkey,
              'mode': 'transit',
              'units': 'imperial'}

    if ampm=='am':
        # add origin, destination, arrival time for AM
        params['origin'] = '{}'.format(record.home_address)
        params['destination'] = '{},{}'.format(record.school_lat, 
                                               record.school_lon)
        
        # format the arrival time to be school session time next Weds
        arr_text = record.am_latest_arr + ' ' + record.tz
        arr_timestamp = convert_times.create_timestamp(arr_text)                                           
        params['arrival_time'] = arr_timestamp

    elif ampm=='pm':
        # add origin, destination, departure time fro PM
        params['origin'] = '{},{}'.format(record.school_lat, 
                                          record.school_lon)
        params['destination'] = '{}'.format(record.home_address)

        # format departure time to be school end bell next Weds
        dep_text = record.pm_earliest_dep + ' ' + record.tz
        dep_timestamp = convert_times.create_timestamp(dep_text)
        params['departure_time'] = dep_timestamp

    return params


def query_dir_api(params):
    r = requests.get(dir_api, params=params)
    time.sleep(.1)
    if r.status_code == 200:
        data = r.json()
    return data


def batch_process(df, ampm):
    all_journeys = []
    for idx, row in df.iterrows():
        print(idx)
        params = format_params(row, ampm)
        response = query_dir_api(params)
        if response['status'] != 'OK':
            response['geocoded_waypoints'][0]['address'] = params['origin']
            response['geocoded_waypoints'][1]['address'] = params['destination']
        all_journeys.append(response)
    return all_journeys


def main():
    full_results = batch_process(od, 'pm')

    with open(pm_out_path, 'w') as out:
        json.dump(full_results, out)
        print('wrote to {}'.format(pm_out_path))


if __name__ == '__main__':
    main()