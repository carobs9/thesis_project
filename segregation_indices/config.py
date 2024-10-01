from pathlib import Path

# Set the root path
# ROOT_PATH = Path('C:/Users/rqg886/Desktop/THESIS_PROJECT')
ROOT_PATH = Path('/Users/caro/Desktop/thesis_project')
FOLDER_PATH = 'segregation_indices'

# general folders
METRO_DATA = ROOT_PATH / 'metro_data' 
MOBILITY_DATA = ROOT_PATH / 'mobility_data' 
DEMOGRAPHIC_DATA = ROOT_PATH / 'demographic_data' 

#subfolders
VIAJES_DATA = MOBILITY_DATA / 'VIAJES' 
PERSONAS_DATA = MOBILITY_DATA / 'PERSONAS'
GEOMETRIA_DATA = MOBILITY_DATA / 'GEOMETRIA' 
ZONIFICACION_DATA = MOBILITY_DATA / 'ZONIFICACION' 

OUTPUTS_PATH = ROOT_PATH / FOLDER_PATH / 'outputs'
INCOME_DATA = ROOT_PATH / FOLDER_PATH / 'data/processed'
FIGURES_PATH = ROOT_PATH / FOLDER_PATH / 'figures'

DATASETS_PATH = ROOT_PATH / 'datasets'

# NOTE: These variables need to be set by the user
# 1. Date of interest

type_of_study = 'month' # 'week', 'weekend', 'month' or 'morans'

# 2. Dynamic figures folder

FIGURES_PATH = FIGURES_PATH / type_of_study

# 3. Variables of interest
INCOME_VARS_OF_INTEREST = ['Media de la renta por unidad de consumo','Mediana de la renta por unidad de consumo',
                           'Renta bruta media por hogar','Renta bruta media por persona',
                            'Renta neta media por hogar', 'Renta neta media por persona ']

# 4. Save figures
SAVE_FIGURES = True