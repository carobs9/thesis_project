import tarfile 
import config as cfg
import matplotlib.pyplot as plt
import pandas as pd
import logging
from utils import open_gz_by_district

# Code to unzip a TAR file on Windows or Mac. NOTE: Run only once to unzip folder from MITMA
# file = tarfile.open('VIAJES/202203_Viajes_distritos.tar') # open file, a zipped folder containing all data monthly (typically in .tar format)
# file.extractall('VIAJES/basicos_distritos_viajes_202203') # extracting file, unzipped folder containing several files
# file.close()

# Configure general logger
logger = logging.getLogger('my_logger')
logger.setLevel(logging.DEBUG)  # Capture all messages from DEBUG and above

# Create a file handler for logging DEBUG and above messages to a file
file_handler = logging.FileHandler('logs/get_viajes.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

# Add the handler to the logger
logger.addHandler(file_handler)


if cfg.type_of_study == 'month': # FIXME: Adapt function to filter more districts easily
    viajes = open_gz_by_district(cfg.VIAJES_DATA / cfg.DF_OF_INTEREST, cfg.MONTH_DAYS, district_code='28079') # substracting trips in Madrid districts during day 7 to 11 of Feb 
elif cfg.type_of_study == 'week':
    viajes = open_gz_by_district(cfg.VIAJES_DATA / cfg.DF_OF_INTEREST, cfg.WEEK_DAYS, district_code='28079') # substracting trips in Madrid districts during day 5 to 6 of Feb 
elif cfg.type_of_study == 'two_weeks':
    viajes = open_gz_by_district(cfg.VIAJES_DATA / cfg.DF_OF_INTEREST, cfg.TWO_WEEK_DAYS, district_code='28079') # substracting trips in Madrid districts during day 5 to 6 of Feb 
elif cfg.type_of_study == 'weekend':
    viajes = open_gz_by_district(cfg.VIAJES_DATA / cfg.DF_OF_INTEREST, cfg.WEEKEND_DAYS, district_code='28079') # substracting trips in Madrid districts during day 5 to 6 of Feb
else:
    print('No time of study has been set')

logger.info(f'Extracting trips from {cfg.DF_OF_INTEREST}')
logger.info(f'Timeframe of study: {cfg.type_of_study}')

if cfg.type_of_study == 'month':
    logger.info(f'Days of interest: {cfg.MONTH_DAYS}')
elif cfg.type_of_study == 'week':
    logger.info(f'Days of interest: {cfg.WEEK_DAYS}')
elif cfg.type_of_study == 'two_weeks':
    logger.info(f'Days of interest: {cfg.TWO_WEEK_DAYS}')
elif cfg.type_of_study == 'weekend':
    logger.info(f'Days of interest: {cfg.WEEKEND_DAYS}')


all_viajes = pd.concat(viajes, ignore_index=True)
print('Shape of data: ', all_viajes.shape)

logger.info(f'Shape of all viajes: {all_viajes.shape}')

if cfg.SAVE_DFS:
    all_viajes.to_csv(f'{cfg.VIAJES_DATA}/viajes_{cfg.type_of_study}_0322.csv', index=False) # saving all trips for week / weekend of interest
    logger.info(f'Figures saved to:{cfg.VIAJES_DATA} / viajes_{cfg.type_of_study}_0322.csv')

#NOTE: The residence of the users in the MITMA data is not by district, but by province. 
# This could be a problem as I am trying to understand how people from different districts move. 
# As a solution, I could filter to only use ‘origen’ == casa or ‘destino’==casa in the districts of Madrid. 
# This way, I could make sure that I am taking a look at those records of people who actually live in a specific district in Madrid.
# The problem is that the mobility would be very limited to those trips either coming from or going home.

filtered_df = all_viajes.loc[(all_viajes['actividad_origen'] == 'casa')]
print('Shape of the data of study (filtering origin=home): ', filtered_df.shape)

logger.info('Done!')