# Functions to geocode files
# This script preps files for create_od_records and gen_transit_isochrones

import configparser
import pandas as pd
import requests
import re

# change these as needed before running the script
school = ''  # if no school identifier exists
school_address_path = 'inputs/indy/indy_schools.csv'
school_out_path = 'outputs/geocoded_indy_schools.csv'
student_address_path = 'inputs/indy/ips_data/IPS Fall 2020-2021 HS.xlsx'
student_out_path = 'temp/indy/hs_walking/more_geocoded_students.csv'

# Google Geocoder API Parameters
g_api = 'https://maps.googleapis.com/maps/api/geocode/json'
config = configparser.ConfigParser()
config.read('config.ini')
gkey = config['auth']['gkey']
gparams = {'key': gkey}


def consolidate_addresses(df):
    """
    Helper function to clean up address fields.
    """
    df['home_address'] = (df['stu_resaddress']
                        + ', Indianapolis, IN')
    return df


def clean_school_name(name_string):
    school_name = name_string.lower()
    # remove numbers and punctuation
    school_name = re.sub('[\d.,-]', '', school_name)
    # trim whitespace
    school_name = school_name.strip()
    # convert remaining spaces to underscores
    school_name = re.sub('[\s/]', '_', school_name)
    school_name = re.sub('@', 'at', school_name)
    return school_name


def rename_school_cols(df):
    """
    Re-map school column names to colnames the scripts use.
    The key column names are campus, am_latest_arr and pm_earliest_dep
    """
    print('renaming')
    school_col_names = {'Priority Order': 'priority',
                        'School/Network': 'school_network',
                        'Campus': 'campus',	
                        'address': 'school_address',
                        'Has Yellow Bus? (Y/N)': 'has_yellow_bus',
                        'AM Bus Arrival': 'am_earliest_arr',
                	    'AM Bell time': 'am_latest_arr',
                        'PM Bell Time':  'pm_earliest_dep',
                        'PM Bus Departure': 'pm_latest_dep'
                    }

    schools = df.rename(columns=school_col_names)
    print(list(schools))
    return schools


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


def batch_geocode(df, address_field):
    results = []
    for idx, row in df.iterrows():
        print(idx)
        results.append(google_geocode_address(row[address_field]))

    lons = pd.Series([i[0] for i in results], name='lon')
    lats = pd.Series([j[1] for j in results], name='lat')
    geocoded_df = pd.concat([df, lats, lons], axis=1)
    return geocoded_df


def process_indy_students():
    """different workflow for indianapolis student file.
    splits the district-wide file by school, geocodes, and saves as individual files.
    """
    data = pd.read_excel(student_address_path, sheet_name=0)
    data = consolidate_addresses(data)

    # split data frame by school code, geocode and write individual school datasets to file
    dfs_by_school = [pd.DataFrame(y) for x, y in data.groupby('stu_sch_code', as_index=False)]
    for df in dfs_by_school:
        #df = batch_geocode(df, 'home_address')
        school_name = list(df['sch_name'].unique())[0]
        school_code = list(df['stu_sch_code'].unique())[0]
        school_name = clean_school_name(str(school_name))
        print(school_name)
        file_name = 'temp/indy/hs_walking/{}_{}_geocoded_students.csv'.format(school_code, school_name)
        df.to_csv(file_name, index=False)

    print('done')


def process_file(address_df, address_field, out_path, call_api=True, cleaning_func=None):
    """
    Perform some cleaning and geocode an address file.
    Args:
      address_df (pandas DataFrame): data frame to geocode
      address_field (str): name of the column in address_df 
          containing the locations to geocode. These do not have to be
          full addresses, but all information to send to google has to
          be in one field. The more complete an address is, the better
          the results.
      out_path (str): where to save the geocoded file to.
      call_api (bool): whether to actually use the geocoding API.
          If False, the data is simply cleaned according to cleaning_func and 
          written to file.
          Useful for student data.
      cleaning_func (function, optional): function to perform additional
          data cleaning before geocoding the file. e.g., to rename fields
          or to combine location information into one column. This function
          should take a pandas DataFrame as an argument.

    Returns:
      None

    Additional output: a csv containing geocoded records
    """
    if cleaning_func:
        address_df = cleaning_func(address_df)
    
    # code to geocode the whole file
    if call_api:
        data = batch_geocode(address_df, address_field)
    data.to_csv(out_path, index=False)
    print('Wrote to {}'.format(out_path))


def main():
    schools = pd.read_csv(school_address_path)
    students = pd.read_excel(student_address_path, sheet_name=0)

    process_file(schools, 
                 'school_address', 
                 school_out_path, 
                 cleaning_func=rename_school_cols)
    process_file(students, 
                 'home_address', 
                 student_out_path, 
                 call_api=False, 
                 cleaning_func=consolidate_addresses)


if __name__ == '__main__':
    main()