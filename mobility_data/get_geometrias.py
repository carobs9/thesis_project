import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import config as cfg
import logging

if cfg.METROPOLITAN==True:

    df = pd.read_csv(r'C:\Users\rqg886\Desktop\thesis_project\segregation_indices\data\raw\income_madrid_metropolitan.csv', sep=';', encoding='latin8')

    nombres_distritos = pd.read_csv(cfg.ZONIFICACION_DATA / 'distritos/nombres_distritos.csv', sep = '|')
    poblacion_distritos = pd.read_csv(cfg.ZONIFICACION_DATA / 'distritos/poblacion_distritos.csv', sep = '|')

    df['ID'] = df['Distritos'].str.split().str[0] # creating ID column
    id_code = '28'
    madrid_ccaa = nombres_distritos[nombres_distritos['ID'].str.startswith(id_code)] # filtering districts within Madrid Comunidad Autonoma
    metropolitan_districts = pd.merge(df, madrid_ccaa, on='ID', how='inner')

    gdf = gpd.read_file(r'C:\Users\rqg886\Desktop\thesis_project\mobility_data\ZONIFICACION\distritos\zonificacion_distritos.shp') # all districts as polygons
    # centroides = gpd.read_file(cfg.ZONIFICACION_DATA / 'distritos/shapes/corrected_zonificacion_distritos_centroides.shp') # all districts as centroids

    metropolitan_gdf = gdf[gdf['ID'].isin(metropolitan_districts['ID'])] # building a gdf containing only districts in the city of Madrid

    if cfg.SAVE_DFS:
        metropolitan_gdf.to_file(cfg.ZONIFICACION_DATA / 'distritos/metropolitan_gdf.geojson', driver="GeoJSON")
        logging.info(f'Saving geodataframe containing geometries of the previously obtained district names to {cfg.ZONIFICACION_DATA}')

else:

    # Configure general logger
    logger = logging.getLogger('my_logger')
    logger.setLevel(logging.DEBUG)  # Capture all messages from DEBUG and above

    # Create a file handler for logging DEBUG and above messages to a file
    file_handler = logging.FileHandler('logs/get_geometrias.log')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

    # Add the handler to the logger
    logger.addHandler(file_handler)


    nombres_distritos = pd.read_csv(cfg.ZONIFICACION_DATA / 'distritos/nombres_distritos.csv', sep = '|')
    poblacion_distritos = pd.read_csv(cfg.ZONIFICACION_DATA / 'distritos/poblacion_distritos.csv', sep = '|')

    # FIXME: Filter more than Madrid districts by changing these lines
    id_code = '28'
    district_code = 'Madrid distrito'
    madrid_ccaa = nombres_distritos[nombres_distritos['ID'].str.startswith(id_code)] # filtering districts within Madrid Comunidad Autonoma
    ciudad_madrid = madrid_ccaa[madrid_ccaa['name'].str.contains(district_code, case=False, na=False)] # filtering only districts from the city of Madrid

    logging.info(f'Filtering names of distritos starting with code {id_code}...')
    logging.info(f'Filtering names of distritos containing {district_code}...')

    # Mapping of district codes to actual district names
    district_mapping = {
        'Madrid distrito 01': 'Centro',
        'Madrid distrito 02': 'Arganzuela',
        'Madrid distrito 03': 'Retiro',
        'Madrid distrito 04': 'Salamanca',
        'Madrid distrito 05': 'Chamartín',
        'Madrid distrito 06': 'Tetuán',
        'Madrid distrito 07': 'Chamberí',
        'Madrid distrito 08': 'Fuencarral-El Pardo',
        'Madrid distrito 09': 'Moncloa-Aravaca',
        'Madrid distrito 10': 'Latina',
        'Madrid distrito 11': 'Carabanchel',
        'Madrid distrito 12': 'Usera',
        'Madrid distrito 13': 'Puente de Vallecas',
        'Madrid distrito 14': 'Moratalaz',
        'Madrid distrito 15': 'Ciudad Lineal',
        'Madrid distrito 16': 'Hortaleza',
        'Madrid distrito 17': 'Villaverde',
        'Madrid distrito 18': 'Villa de Vallecas',
        'Madrid distrito 19': 'Vicálvaro',
        'Madrid distrito 20': 'San Blas-Canillejas',
        'Madrid distrito 21': 'Barajas'
    }

    # Adding a new column with the actual district name
    logging.info('Mapping ugly names to actual comercial names...')
    ciudad_madrid.loc[:, 'name_2'] = ciudad_madrid['name'].map(district_mapping)

    if cfg.SAVE_DFS:
        ciudad_madrid.to_csv(cfg.ZONIFICACION_DATA / 'distritos/PROCESSED_nombres_distritos.csv', index=False)
        logging.info(f'Saving dataframe containing names of districts to {cfg.ZONIFICACION_DATA}')

    gdf = gpd.read_file(cfg.ZONIFICACION_DATA / 'distritos/shapes/zonificacion_distritos.shp') # all districts as polygons
    # centroides = gpd.read_file(cfg.ZONIFICACION_DATA / 'distritos/shapes/corrected_zonificacion_distritos_centroides.shp') # all districts as centroids

    madrid_city_gdf = gdf[gdf['ID'].isin(ciudad_madrid['ID'])] # building a gdf containing only districts in the city of Madrid
    # madrid_city_centroids = centroides[centroides['ID'].isin(ciudad_madrid['ID'])] # building a gdf containing only districts in the city of Madrid

    if cfg.SAVE_DFS:
        madrid_city_gdf.to_file(cfg.ZONIFICACION_DATA / 'distritos/madrid_gdf.geojson', driver="GeoJSON")
        logging.info(f'Saving geodataframe containing geometries of the previously obtained district names to {cfg.ZONIFICACION_DATA}')

    ax = madrid_city_gdf.plot(color='blue', figsize=(5, 5)) # testing results

    logging.info('Done!')