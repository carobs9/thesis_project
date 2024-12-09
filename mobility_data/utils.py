import pandas as pd
import os

def get_overview(directory):
    '''
    Function to get an idea of the shape of different dataframes (.gz format) contained in the viajes, personas or pernoctaciones folder.
    Overview(str): Name of the folder of interest (personas, viajes, pernoctaciones)
    '''
    files = [f for f in os.listdir(directory) if f.endswith('.csv.gz')]
    for file in files:
        try:
            df = pd.read_csv(os.path.join(directory, file), compression='gzip', sep='|')
            print(f"File: {file}")
            print(f" - Shape: {df.shape}")
        except Exception as e:
            print(f"Error reading {file}: {e}")

def open_gz(data_dir, days):
    '''
    Function to open data from specific days from personas, viajes, or pernoctaciones stored as .gz format.
    data_dir (str): Directory of the folder containing personas, viajes or pernoctaciones.
    days (list of int): List of indices indicating the days of the month (i.e. 10 means day 11).
    Returns:
        A list of dataframes containing the concatenated data for the specified days.
    '''
    all_files = [f for f in os.listdir(data_dir) if f.endswith('.csv.gz')] # List all files in the directory and filter for .csv.gz files
    all_files_sorted = sorted(all_files) # Sort the files list to ensure they are in chronological order

    dfs = []  # Initialize a list to store DataFrames
    for day in days: # Iterate over the list of days
        file_to_open = all_files_sorted[day] # Select the file for the given day (day should be zero-based index)
        file_path = os.path.join(data_dir, file_to_open)  # Create the full path to the file
        df = pd.read_csv(file_path, compression='gzip', sep='|',decimal='.') # Read the compressed CSV file
        dfs.append(df) # Append the DataFrame to the list
    
    return dfs

def filter_district(df, district_code):
    '''Function to filter data from a specific district from personas, viajes or pernoctaciones.
    Data(str): personas, viajes, pernoctaciones.
    District code (str): District code to filter by. For example, districts of the city of Madrid start with 28079
    '''
    filtered_data = df[df['origen'].str.startswith(district_code) & df['destino'].str.startswith(district_code)]
    return filtered_data

def open_gz_by_district(data_dir, days, district_code=None):
    '''
    Function to open data from specific days from personas, viajes, or pernoctaciones stored as .gz format.
    data_dir (str): Directory of the folder containing personas, viajes or pernoctaciones.
    days (list of int): List of indices indicating the days of the month (i.e. 10 means day 11).
    district_code (str, optional): District code to filter by while reading the files. For example, '28079' for Madrid districts.
    Returns:
        A list of dataframes containing the concatenated data for the specified days.
    '''
    all_files = [f for f in os.listdir(data_dir) if f.endswith('.csv.gz')]  # List all files in the directory and filter for .csv.gz files
    all_files_sorted = sorted(all_files)  # Sort the files list to ensure they are in chronological order

    dfs = []  # Initialize a list to store DataFrames
    for day in days:  # Iterate over the list of days
        file_to_open = all_files_sorted[day]  # Select the file for the given day (day should be zero-based index)
        file_path = os.path.join(data_dir, file_to_open)  # Create the full path to the file

        # Read the entire file into a DataFrame
        df = pd.read_csv(file_path, compression='gzip', sep='|', decimal='.')

        # Convert 'origen' and 'destino' columns to strings, filling NaN values with empty strings
        df['origen'] = df['origen'].astype(str).fillna('')
        df['destino'] = df['destino'].astype(str).fillna('')

        # If a district code is provided, filter the DataFrame
        if district_code:
            df = df[df['origen'].str.startswith(district_code) & df['destino'].str.startswith(district_code)]

        # Append the filtered DataFrame to the list
        dfs.append(df)

    return dfs

