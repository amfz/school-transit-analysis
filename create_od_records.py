# Merge school and student data to create a dataset to use in directions API calls
# Script builds off of the outputs of geocode_and_prep
# Assumes the student data has a field called "home_address"
# And the school data has a field called "school_address"
# Before running single process, confirm join fields in line 61 are correct

import pandas as pd
import os
import re

# only useful for path completion when single-processing
# ignore this variable when batch processing
school = ''

student_data_path = 'temp/indy/{}_geocoded_students.csv'.format(school)
school_data_path = 'outputs/geocoded_indy_schools.csv'
combined_output_path = 'temp/indy/{}_od_df.csv'.format(school)

def batch_combine(directory):
    """
    Go through the given directory and all its subfolders,
    creating origin-destination files for each file ending in "geocoded_students.csv"
    """
    schools = pd.read_csv(school_data_path)
    schools = schools.rename(columns={'address': 'school_address',
                                      'lat': 'school_lat',
                                      'lon': 'school_lon'})
    
    # walk through the indy temp folder
    for subdir, dirs, files in os.walk(directory):
        for f in files:
            # only process schools with program codes
            if re.search('^\d', f) and f.endswith('geocoded_students.csv'):
                # create the output file name
                file_stem = re.search('\w+', f).group()[:-17]
                file_name = '{}od_df.csv'.format(file_stem)
                out_file = os.path.join(subdir, file_name)
                print(out_file)

                # perform the join
                students = pd.read_csv(os.path.join(subdir, f))
                students = students.rename(columns={'lat': 'home_lat',
                                                    'lon': 'home_lon'})
                joined = students.merge(schools, 
                                        left_on='stu_sch_code', 
                                        right_on='school_code')
                joined.to_csv(out_file, index=False)


def main():
    # if there are join issues, try setting read_csv's dtype argument
    schools = pd.read_csv(school_data_path, 
                          dtype={'school_code': str})
    schools = schools.rename(columns={'address': 'school_address',
                                      'lat': 'school_lat',
                                      'lon': 'school_lon'})
    students = pd.read_csv(student_data_path, 
                           dtype={'stu_school_code': str})
    students = students.rename(columns={'lat': 'home_lat',
                                        'lon': 'home_lon'})

    # make sure join columns are correct
    joined = students.merge(schools, left_on='stu_sch_code', right_on='school_code')
    joined.to_csv(combined_output_path, index=False)


if __name__ == '__main__':
    main()