import configparser
import requests
import pandas as pd

address_path = 'inputs/master-school-list-copy.csv'
config = configparser.ConfigParser()
config.read('config.ini')
gkey = config['auth']['gkey']
g_api = 'https://maps.googleapis.com/maps/api/geocode/json'
c_api = 'https://geocoding.geo.census.gov/geocoder/locations/onelineaddress'

gparams = {'key': gkey}
cparams = {'benchmark': 8, 'format':'json'}

def rename_school_cols(df):
    school_col_names = {'Priority Order': 'priority',
                        'School/Network': 'school_network',
                        'Campus': 'campus',	
                        'Address': 'address',
                        'Has Yellow Bus? (Y/N)': 'has_yellow_bus',
                        'AM Earliest Arrival\n(15 min early)': 'am_earliest_arr',
                	    'AM Arrival Target (Latest)': 'am_latest_arr',
                        'PM Departure Target (Earliest)':  'pm_earliest_dep',
                        'PM Latest Departure (15 min late)': 'pm_latest_dep'
                    }

    schools = df.rename(columns=school_col_names)
    return schools


def census_geocode_address(addy):
    ans = (None, None)
    cparams['address'] = addy
    r = requests.get(c_api, params=cparams)
    if r.status_code == 200:
        data = r.json()
        matches = data['result']['addressMatches']
        if len(matches) > 0:
            coords = data['result']['addressMatches'][0]['coordinates']
            ans = (coords['x'], coords['y'])
    return ans


def google_geocode_address(addy):
    ans = (None, None)
    gparams['address'] = addy
    r = requests.get(g_api, params=gparams)
    if r.status_code == 200:
        data = r.json()
        results = data['results']
        if len(results) > 0:
            coords = results[0]['geometry']['location']
            ans = (coords['lng'], coords['lat'])
    return ans


def main():
    addys = pd.read_csv(address_path)
    addys = rename_school_cols(addys)
    results = []

    for idx, row in addys.iterrows():
        results.append(google_geocode_address(row.address))

    lons = pd.Series([i[0] for i in results], name='school_lon')
    lats = pd.Series([j[1] for j in results], name='school_lat')
    geocoded_df = pd.concat([addys, lats, lons], axis=1)
    geocoded_df.to_csv('outputs/geocoded_schools.csv', index=False)


if __name__ == '__main__':
    main()