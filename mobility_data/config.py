from pathlib import Path

# Set the root path
# ROOT_PATH = Path('C:/Users/rqg886/Desktop/THESIS_PROJECT')
ROOT_PATH = Path('/Users/caro/Desktop/thesis_project')
FOLDER_PATH = 'mobility_data'

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
FIGURES_PATH = ROOT_PATH / FOLDER_PATH / 'figures'

DATASETS_PATH = ROOT_PATH / 'datasets'

# NOTE: These variables need to be set by the user
# 1. Date of interest (week/weekend, specific days)

type_of_study = 'week' # or 'weekend', or 'morans'
WEEK_DAYS =  [6,7,8,9,10] # days of the month to study (normal week)
WEEKEND_DAYS =  [4,5] # days of the month to study (normal weekend)

# 2. Dataframe of interest
DF_OF_INTEREST = 'basicos_distritos_viajes_202202' # change accordningly: 'basicos_distritos_viajes_yyyymm'

# 3. Dynamic figures folder

FIGURES_PATH = FIGURES_PATH / type_of_study

# 4. Save figures
SAVE_FIGURES = True

# 5. Save dataframes
SAVE_DFS = False