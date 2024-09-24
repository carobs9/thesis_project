# Code to unzip a TAR file on Windows or Mac. NOTE: Run only once to unzip
import tarfile 
# file = tarfile.open('VIAJES/202202_Viajes_distritos.tar') # open file, a zipped folder containing all data monthly (typically in .tar format)
# file.extractall('VIAJES/basicos_distritos_viajes_202202') # extracting file, unzipped folder containing several files
# file.close() 

import config as cfg
import matplotlib.pyplot as plt
import pandas as pd
from utils import get_overview, open_gz, open_gz_by_district, filter_district

if cfg.type_of_study == 'week':
    viajes = open_gz_by_district(cfg.VIAJES_DATA / 'basicos_distritos_viajes_202202', [6,7,8,9,10], district_code='28079') # substracting trips in Madrid districts during day 7 to 11 of Feb 
elif cfg.type_of_study == 'weekend':
    viajes = open_gz_by_district(cfg.VIAJES_DATA / 'basicos_distritos_viajes_202202', [4,5], district_code='28079') # substracting trips in Madrid districts during day 5 to 6 of Feb 
else:
    print('No time of study has been set')

all_viajes = pd.concat(viajes, ignore_index=True)
print('Shape of data: ', all_viajes.shape)

all_viajes.to_csv('viajes/all_viajes_week_0222.csv', index=False) # saving all trips for week / weekend of interest

#NOTE: The residence of the users in the MITMA data is not by district, but by province. 
# This could be a problem as I am trying to understand how people from different districts move. 
# As a solution, I could filter to only use ‘origen’ == casa or ‘destino’==casa in the districts of Madrid. 
# This way, I could make sure that I am taking a look at those records of people who actually live in a specific district in Madrid.
# The problem is that the mobility would be very limited to those trips either coming from or going home.
filtered_df = all_viajes.loc[(all_viajes['actividad_origen'] == 'casa')]

print('Shape of the data of study (filtering origin=home): ', filtered_df.shape)