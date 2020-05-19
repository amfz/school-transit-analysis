import pandas as pd

student_data_path = 'inputs/elpaso/geocoded_students.csv'
school_data_path = 'outputs/geocoded_schools.csv'
combined_output_path = 'inputs/elpaso/od_df.csv'

def main():
    students = pd.read_csv(student_data_path)
    schools = pd.read_csv(school_data_path)
    joined = students.merge(schools, left_on='school', right_on='campus')
    joined.to_csv(combined_output_path, index=False)

if __name__ == '__main__':
    main()