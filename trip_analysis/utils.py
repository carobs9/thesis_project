import pandas as pd

# DEFINING LABELS OF NODES 
district_mapping = pd.read_csv('/Users/caro/Desktop/thesis_project/data_overview/outputs/districts_and_population.csv')
id_to_name = district_mapping.set_index('ID')['name_2'].to_dict()


# TRIP ANALYSIS --------------------------------------------------------------------------------------------------- 

def build_trip_count(df, sociodemographic_var=None):
    # Determine the grouping columns based on whether sociodemographic_var is provided
    grouping_columns = ['origen', 'destino']
    if sociodemographic_var:
        grouping_columns.append(sociodemographic_var)
    
    # Group by the determined columns and calculate the trip count
    trip_counts = df.groupby(grouping_columns).size().reset_index(name='trip_count')
    return trip_counts

def get_district_names(trip_counts):
    # get names of districts
    trip_counts = trip_counts.merge(district_mapping[['ID', 'name_2']], how='left', left_on='origen', right_on='ID')
    trip_counts = trip_counts.rename(columns={'name_2': 'origin'})
    trip_counts = trip_counts.merge(district_mapping[['ID', 'name_2']], how='left', left_on='destino', right_on='ID')
    trip_counts = trip_counts.rename(columns={'name_2': 'destination'})

    # drop extra columns
    trip_counts = trip_counts.drop(columns=['ID_x', 'ID_y'])

    return trip_counts

def normalize_by_pop(trip_counts, population_df):
    trip_counts = trip_counts.merge(population_df, left_on='origen', right_on='ID', how='left')
    # Normalize trip counts by population of the origin district
    trip_counts['normalized_trip_count'] = trip_counts['trip_count'] / trip_counts['Population']
    trip_counts.drop(columns=['ID','Population'], inplace=True)  # removing extra columns
    return trip_counts



def get_income_data(trip_counts, income, income_var_1, income_var_2):
    # get origin incomes
    trip_counts = trip_counts.merge(
    income[['ID', income_var_1, income_var_2]], 
    left_on='origen', 
    right_on='ID', 
    how='left'
)
    # rename
    trip_counts.rename(columns={income_var_1: f'Origin {income_var_1}'}, inplace=True)
    trip_counts.rename(columns={income_var_2: f'Origin {income_var_2}'}, inplace=True)

    # drop extra columns
    trip_counts.drop(columns=['ID'], inplace=True)

    # get destination incomes
    trip_counts = trip_counts.merge(
        income[['ID', income_var_1, income_var_2]], 
        left_on='destino', 
        right_on='ID', 
        how='left'
    )

    # rename columns
    trip_counts.rename(columns={income_var_1: f'Destination {income_var_1}'}, inplace=True)
    trip_counts.rename(columns={income_var_2: f'Destination {income_var_2}'}, inplace=True)
    # drop extra columns
    trip_counts.drop(columns=['ID', 'origen', 'destino'], inplace=True)

    return trip_counts

def add_quantiles(trip_counts, income_var, n_quantiles=6):
    trip_counts[f'income decile origin {income_var}'] = pd.qcut(trip_counts[f'Origin {income_var}'], n_quantiles, labels=False, duplicates='drop')
    trip_counts[f'income decile destination {income_var}'] = pd.qcut(trip_counts[f'Destination {income_var}'], n_quantiles, labels=False, duplicates='drop') 
    return trip_counts