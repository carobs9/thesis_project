import config as cfg
import pandas as pd 
import geopandas as gpd

nombres_distritos = pd.read_csv(cfg.ZONIFICACION_DATA / 'distritos/PROCESSED_nombres_distritos.csv')
gdf = gpd.read_file(cfg.ZONIFICACION_DATA / 'distritos/madrid_gdf.geojson')
renta = pd.read_csv('segregation_indices/data/raw/indicadores_renta_2_2021.csv', sep=';') # SOURCE = https://ine.es/jaxiT3/Datos.htm?t=31097

renta['ID'] = renta['Distritos'].str[:7]
renta.drop(columns=['Distritos', 'Municipios', 'Secciones'], inplace=True)

renta_pivot = renta.pivot(index='ID', columns='Indicadores de renta media y mediana', values='Total').reset_index()
renta_pivot.columns.name = None  # Remove the column grouping label
renta_pivot['ID'] = renta_pivot['ID'].astype('int64')
gdf['ID'] = gdf['ID'].astype('int64')

merged = pd.merge(renta_pivot, gdf, on='ID', how='inner') # merging the income and geography data into one gdf
merged = gpd.GeoDataFrame(merged, geometry='geometry')
merged = merged.set_crs(gdf.crs)

merged = merged.rename(columns={ # translating
    'Media de la renta por unidad de consumo': 'Average income per consumption unit',
    'Mediana de la renta por unidad de consumo': 'Median income per consumption unit',
    'Renta bruta media por hogar': 'Average gross income per household',
    'Renta bruta media por persona': 'Average gross income per person',
    'Renta neta media por hogar': 'Average net income per household',
    'Renta neta media por persona ': 'Average net income per person'
})

merged.to_file("segregation_indices/data/processed/geometries_and_income.geojson", driver="GeoJSON")