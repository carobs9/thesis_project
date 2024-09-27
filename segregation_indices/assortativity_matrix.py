import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import config as cfg
import pandas as pd
import geopandas as gpd
import sys
import logging

# Configure general logger
logger = logging.getLogger('my_logger')
logger.setLevel(logging.DEBUG)  # Capture all messages from DEBUG and above

# Create a file handler for logging DEBUG and above messages to a file
file_handler = logging.FileHandler('logs/assortativity_matrix.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

# Add the handler to the logger
logger.addHandler(file_handler)

# SET VARIABLES -----------------------------------------------------------------

# FIXME: Make more efficient, and fix variable names to plot nicely
var_of_interest = 'Renta bruta media por hogar' 
n_income_deciles = 10

if cfg.type_of_study == 'week':
    time_of_study = 'Normal Week'
elif cfg.type_of_study == 'weekend':
    time_of_study = 'Normal Weekend'
else:
    print('No correct time of study has been set. Maybe you meant week or weekend?')

logger.info(f'I calculate {n_income_deciles} income deciles for different income data in the city of Madrid')
logger.info(f'Timeframe: {time_of_study}')
logger.info(f'I build assortativity matrices for the {var_of_interest}')
logger.info(f'The variables for which income deciles are calculared are: {cfg.INCOME_VARS_OF_INTEREST}')
logger.info(f'Save figures = {cfg.SAVE_FIGURES}')
logger.info(f'Figures path: {cfg.FIGURES_PATH}')

# OPEN DATA ----------------------------------------------------------------------

logger.info('Opening data...')

rent_data = gpd.read_file(cfg.INCOME_DATA / 'geometries_and_income.geojson') # rent data to add to the viajes data to find income per district
rent_data = rent_data[['ID', 'geometry'] + cfg.INCOME_VARS_OF_INTEREST ] # here I select the variables of interest

if cfg.type_of_study == 'week':
    file_name = 'all_viajes_week_0222.csv'
elif cfg.type_of_study == 'weekend':
    file_name = 'all_viajes_weekend_0222.csv'
else:
    file_name = 'default_file.csv'  # FIXME: Fallback option if neither is True

week = pd.read_csv(cfg.MOBILITY_DATA / f'VIAJES/{file_name}') # week of interest
week = week.loc[(week['actividad_origen'] == 'casa')] # filtering only trips from home!

logger.info(f"Dataframes used: {cfg.INCOME_DATA / 'geometries_and_income.geojson'} and {cfg.MOBILITY_DATA / f'VIAJES/{file_name}'}")
logger.info('Shape of the rent dataset: %s', rent_data.shape)
logger.info('Shape of the mobility dataset: %s', week.shape)

# MERGE INCOME AND MOBILITY DATA ----------------------------------------------------------------------

logger.info('1. Merging mobility and income data')
# 1. Adding income data per district to the mobility data, to later calculate deciles and build assortativity matrix
viajes_with_income = pd.merge(
    week,
    rent_data,
    left_on='origen',  # The cleaned 'origen' from viajes DataFrame
    right_on='ID',  # The 'ID' from gdf
    how='left'  # Perform a left join to keep all rows from viajes
)

logger.info(f'Variable to calculate matrices on is set to: {var_of_interest}')

# CALCULATE INCOME DECILES ----------------------------------------------------------------------

logger.info(f'2. Calculating {n_income_deciles} income deciles for the {var_of_interest} data.')

# 2. Divide data into income deciles D for each SE class - for each origin and destination, I add the income decile 
rent_data['income_decile'] = pd.qcut(rent_data[var_of_interest], n_income_deciles, labels=False)

# Add deciles to dataframe
viajes_with_income = pd.merge(viajes_with_income, rent_data[['ID', 'income_decile']], 
                              left_on='origen', right_on='ID', how='left', suffixes=('', '_origin'))

viajes_with_income = pd.merge(viajes_with_income, rent_data[['ID', 'income_decile']], 
                              left_on='destino', right_on='ID', how='left', suffixes=('', '_dest'))
# Clean dataframe 
viajes_with_income.drop(columns=['residencia', 'estudio_origen_posible', 'estudio_origen_posible', 'ID', 'ID_origin', 'ID_dest'], inplace=True)

# PLOT INCOME DECILES -----------------------------------------------------------------------------------------------

logger.info('Plotting income deciles')
bin_counts = viajes_with_income['income_decile'].value_counts().sort_index()
bin_counts.plot(kind='bar')

# 1. matplotlib. FIXME: IS this plot correct? I have to make sure it makes sense.
plt.xlabel('Income Bin')
plt.ylabel('Number of Entries')
plt.title(f'Distribution of Deciles for Destination of Trips\n{time_of_study}\nVariable: {var_of_interest.lower()}')

# 2. plotly
fig = px.bar(
    x=bin_counts.index,  # The 'Income Bin' values
    y=bin_counts.values,  # The 'Number of Entries' values
    labels={'x': 'Income Bin', 'y': 'Number of Entries'},
    title=f'Distribution of {var_of_interest} Deciles for Destination of Trips\n{time_of_study}'
)

if cfg.SAVE_FIGURES:
    fig.write_html(str(cfg.FIGURES_PATH / f'{var_of_interest.lower()}_deciles_distribution_destination.html'))
    plt.savefig(cfg.FIGURES_PATH / f'{var_of_interest.lower()}_deciles_distribution_destination.png', dpi=300, bbox_inches='tight')
    logger.info(f"Plot saved at: {cfg.FIGURES_PATH / f'{var_of_interest.lower()}_deciles_distribution_destination.png'}")

logger.info(f'Income deciles for {cfg.INCOME_VARS_OF_INTEREST} saved!')

# BUILD ASSORTATIVITY MATRICES ----------------------------------------------------------------------------------------

logger.info('Building assortativity matrices...')

# Group by origin and destination deciles and count the trips
trip_counts_by_decile = viajes_with_income.groupby(['renta', 'income_decile', 'income_decile_dest']).size().reset_index(name='trip_count')
districts = rent_data['ID'].unique()

try:
    # Try using pivot() if there are no duplicate index/column combinations
    assortativity_matrix = trip_counts_by_decile.pivot(
        index='income_decile', 
        columns='income_decile_dest', 
        values='trip_count'
    ).fillna(0)

except ValueError as e:
    # If there's a ValueError (likely due to duplicate index/column pairs), fallback to pivot_table()
    logger.debug(f"Encountered an error with pivot(): {e}")
    logger.debug("Switching to pivot_table() to handle duplicates.")
    
    # Use pivot_table() with aggregation to handle duplicates
    assortativity_matrix = trip_counts_by_decile.pivot_table(
        index='income_decile', 
        columns='income_decile_dest', 
        values='trip_count', 
        aggfunc='sum',  # Aggregate duplicates by summing trip counts
        fill_value=0  # Fill missing values with 0
    )

logger.info("Assortativity matrix created successfully!")

# Normalize 
assortativity_matrix_normalized = assortativity_matrix.div(assortativity_matrix.sum(axis=1), axis=0)

logger.info("Assortativity matrix normalized successfully!")

# PLOT AND SAVE ASSORTATIVITY MATRICES --------------------------------------------------------------------------------------

plt.figure(figsize=(10, 8))
sns.heatmap(assortativity_matrix, annot=False, cmap='viridis', cbar_kws={'label': 'Number of Trips'}, fmt=".2f")
plt.title(f'Assortativity Matrix of Trips Between Deciles\n{time_of_study}\nVariable: {var_of_interest}')
plt.xlabel('Destination District SES')
plt.ylabel('Home District SES')

if cfg.SAVE_FIGURES:
    plt.savefig(cfg.FIGURES_PATH / f'Assortativity Matrix of Trips Between {var_of_interest} Deciles, Normal Week February 2022.png', dpi=300, bbox_inches='tight')
    logger.info(f"Plot saved at: {cfg.FIGURES_PATH / f'Assortativity Matrix of Trips Between {var_of_interest} Deciles, Normal Week February 2022.png'}")

plt.figure(figsize=(10, 8))
sns.heatmap(assortativity_matrix_normalized, annot=False, cmap='viridis', cbar_kws={'label': 'Normalized Probability'}, fmt=".2f")
plt.title(f'Normalized Assortativity Matrix of Trips Between Deciles\n{time_of_study}\nVariable: {var_of_interest}')
plt.xlabel('Destination District SES')
plt.ylabel('Home District SES')   

if cfg.SAVE_FIGURES:
    plt.savefig(cfg.FIGURES_PATH / f'Normalized Assortativity Matrix of Trips Between {var_of_interest} Deciles, Normal Week February 2022.png', dpi=300, bbox_inches='tight')
    logger.info(f"Plot saved at: {cfg.FIGURES_PATH / f'Normalized Assortativity Matrix of Trips Between {var_of_interest} Deciles, Normal Week February 2022.png'}")

logger.info(f"Assortativity matrix figures for {var_of_interest} saved successfully!")

# STRATIFY MOBILITY DATA BY RENT ----------------------------------------------------------------------------------

middle = trip_counts_by_decile[trip_counts_by_decile['renta']=='10-15']
high = trip_counts_by_decile[trip_counts_by_decile['renta']=='>15']

assortativity_matrix_middle = middle.pivot(index='income_decile', columns='income_decile_dest', values='trip_count').fillna(0)
assortativity_matrix_middle_normalized = assortativity_matrix_middle.div(assortativity_matrix_middle.sum(axis=1), axis=0)

assortativity_matrix_high = high.pivot(index='income_decile', columns='income_decile_dest', values='trip_count').fillna(0)
assortativity_matrix_high_normalized = assortativity_matrix_high.div(assortativity_matrix_high.sum(axis=1), axis=0)

logger.info('Stratifying mobility data by rent...')
logger.debug('Put more thought into this, and review')

# PLOT ASSORTATIVITY MATRICES STRATIFIED BY RENT ------------------------------------------------------------------

logger.info('Plotting assortativity matrices stratified by rent...')

plt.figure(figsize=(10, 8))
sns.heatmap(assortativity_matrix_middle_normalized, annot=False, cmap='viridis', cbar_kws={'label': 'Normalized Probability'}, fmt=".2f")
plt.title(f'Assortativity Matrix of Trips Between Deciles, Income Bracket 10-15\n{time_of_study}\nVariable: {var_of_interest}')
plt.xlabel('Destination District SES')
plt.ylabel('Home District SES')

if cfg.SAVE_FIGURES:
    plt.savefig(cfg.FIGURES_PATH /f'Assortativity Matrix of Trips Between {var_of_interest} Deciles, Normal Week February 2022, Income Bracket 10-15.png', dpi=300, bbox_inches='tight')
    logger.info(f"Plot saved at: {cfg.FIGURES_PATH /f'Assortativity Matrix of Trips Between {var_of_interest} Deciles, Normal Week February 2022, Income Bracket 10-15.png'}")

plt.figure(figsize=(10, 8))
sns.heatmap(assortativity_matrix_high_normalized, annot=False, cmap='viridis', cbar_kws={'label': 'Normalized Probability'}, fmt=".2f")
plt.title(f'Assortativity Matrix of Trips Between Deciles,  Income Bracket >15\n{time_of_study}\nVariable: {var_of_interest}')
plt.xlabel('Destination District SES')
plt.ylabel('Home District SES')

if cfg.SAVE_FIGURES:
    plt.savefig(cfg.FIGURES_PATH /f'Assortativity Matrix of Trips Between {var_of_interest} Deciles, Normal Week February 2022, Income Bracket Over 15.png', dpi=300, bbox_inches='tight')
    logger.info(f"Plot saved at: {cfg.FIGURES_PATH /f'Assortativity Matrix of Trips Between {var_of_interest} Deciles, Normal Week February 2022, Income Bracket Over 15.png'}")

logger.info(f'Assortativity matrices for {var_of_interest} saved!')
sys.exit("Stopping the script")