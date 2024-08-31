import pandas as pd
import os

def get_overview(directory):
    '''
    Function to get an idea of the shape of different dataframes (.gz format) contained in the viajes, personas or pernoctaciones folder.
    Overview(str): Name of the folder of interest (personas, viajes, pernoctaciones)'''
    files = [f for f in os.listdir(directory) if f.endswith('.csv.gz')]
    for file in files:
        try:
            df = pd.read_csv(os.path.join(directory, file), compression='gzip', sep='|')
            print(f"File: {file}")
            print(f" - Shape: {df.shape}")
        except Exception as e:
            print(f"Error reading {file}: {e}")

def open_gz(data_dir, day):
    '''Function to open data from a specific day from personas, viajes or pernoctaciones stored as .gz format.
    Data:dir(str): directory of the folder containing personas, viajes, pernoctaciones.
    Day (int): Index of the dataframe indicating the day of the month (i.e. 10 means day 11)'''
    # List all files in the directory and filter for .csv.gz files
    all_files = [f for f in os.listdir(data_dir) if f.endswith('.csv.gz')]
    # Sort the files list to ensure they are in chronological order
    all_files_sorted = sorted(all_files)
    # Select the file for the given day (day should be zero-based index)
    file_to_open = all_files_sorted[day]
    # Create the full path to the file
    file_path = os.path.join(data_dir, file_to_open)
    # Read the compressed CSV file
    df = pd.read_csv(file_path, compression='gzip', sep='|')
    return df

def filter_district(df, district_code):
    '''Function to filter data from a specific district from personas, viajes or pernoctaciones.
    Data(str): personas, viajes, pernoctaciones.
    District code (str): District code to filter by. For example, districts of the city of Madrid start with 28079'''
    filtered_data = df[df['origen'].str.startswith(district_code) & df['destino'].str.startswith(district_code)]
    return filtered_data