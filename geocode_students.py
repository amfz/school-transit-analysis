import configparser
import pandas as pd
import requests

# change these as needed before running the script
school = 'El Paso Leadership Academy'
student_address_path = 'inputs/elpaso/student_addresses.xlsx'
out_path = 'inputs/elpaso/geocoded_students.csv'

g_api = 'https://maps.googleapis.com/maps/api/geocode/json'
config = configparser.ConfigParser()
config.read('config.ini')
gkey = config['auth']['gkey']
gparams = {'key': gkey}


def consolidate_addresses(df):
    df['home_address'] = (df['P Num'].astype(str)
                        + ' ' 
                        + df['P St.'] 
                        + ', ' 
                        + df['P City'] 
                        + ', ' 
                        + df['P State']
                        + ' '
                        + df['P Zip'])
    print(df.head())
    return df


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


def batch_geocode(df):
    results = []
    for idx, row in df.iterrows():
        results.append(google_geocode_address(row.home_address))

    lons = pd.Series([i[0] for i in results], name='home_lon')
    lats = pd.Series([j[1] for j in results], name='home_lat')
    geocoded_df = pd.concat([df, lats, lons], axis=1)
    return geocoded_df


def main():
    data = pd.read_excel(student_address_path,
                         dtype={'P Zip': str})
    data = consolidate_addresses(data)
    data = batch_geocode(data)
    data['school'] = school
    data.to_csv(out_path, index=False)
    print('done')


if __name__ == '__main__':
    main()