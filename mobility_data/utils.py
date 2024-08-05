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

def open_gz(data, day):
    '''Function to open data from a specific day from personas, viajes or pernoctaciones stored as .gz format.
    Data(str): personas, viajes, pernoctaciones.
    Day (int): Index of the dataframe indicating the day of the month (i.e. 10 means day 11)'''
    df = pd.read_csv(os.path.join(data, [f for f in os.listdir(data) if f.endswith('.csv.gz')][day]), compression='gzip', sep='|')
    return df