import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import config as cfg

nombres_distritos = pd.read_csv(cfg.ZONIFICACION_DATA / 'distritos/nombres_distritos.csv', sep = '|')
poblacion_distritos = pd.read_csv(cfg.ZONIFICACION_DATA / 'distritos/poblacion_distritos.csv', sep = '|')

# FIXME: Filter more than Madrid districts by changing these lines
madrid_ccaa = nombres_distritos[nombres_distritos['ID'].str.startswith("28")] # filtering districts within Madrid Comunidad Autonoma
ciudad_madrid = madrid_ccaa[madrid_ccaa['name'].str.contains("Madrid distrito", case=False, na=False)] # filtering only districts from the city of Madrid

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
ciudad_madrid['name_2'] = ciudad_madrid['name'].map(district_mapping)

# ciudad_madrid.to_csv(zonificacion_data / 'distritos/PROCESSED_nombres_distritos.csv', index=False)

gdf = gpd.read_file(cfg.ZONIFICACION_DATA / 'distritos/zonificacion_distritos.shp') # all districts as polygons
centroides = gpd.read_file(cfg.ZONIFICACION_DATA / 'distritos/zonificacion_distritos_centroides.shp') # all districts as centroids

madrid_city_gdf = gdf[gdf['ID'].isin(ciudad_madrid['ID'])] # building a gdf containing only districts in the city of Madrid
madrid_city_centroids = centroides[centroides['ID'].isin(ciudad_madrid['ID'])] # building a gdf containing only districts in the city of Madrid

# madrid_city_gdf.to_file(zonificacion_data / 'distritos/madrid_gdf.geojson', driver="GeoJSON")

ax = madrid_city_gdf.plot(color='blue', figsize=(5, 5)) # testing results