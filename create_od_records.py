import pandas as pd

school = 'yellowstone_schools'

student_data_path = 'inputs/houston/{}/geocoded_students.csv'.format(school)
school_data_path = 'outputs/geocoded_schools.csv'
combined_output_path = 'inputs/houston/{}/od_df.csv'.format(school)

def main():
    students = pd.read_csv(student_data_path)
    schools = pd.read_csv(school_data_path)
    schools = schools.rename(columns={'address': 'school_address'})
    joined = students.merge(schools, left_on='campus', right_on='campus')
    joined.to_csv(combined_output_path, index=False)

if __name__ == '__main__':
    main()