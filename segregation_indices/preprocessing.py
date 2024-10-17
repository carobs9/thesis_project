import config as cfg
import pandas as pd 
import geopandas as gpd

def remove_thousands_separator(value):
    # Remove dots and convert to integer
    return int(value.replace('.', ''))

nombres_distritos = pd.read_csv(cfg.ZONIFICACION_DATA / 'distritos/PROCESSED_nombres_distritos.csv')
gdf = gpd.read_file(cfg.ZONIFICACION_DATA / 'distritos/madrid_gdf.geojson')
renta = pd.read_csv( # SOURCE = https://ine.es/jaxiT3/Datos.htm?t=31097
    'data/raw/indicadores_renta_2_2021.csv', 
    sep=';', 
    converters={
        'Total': remove_thousands_separator,
    })
gini_index = pd.read_csv('segregation_indices/data/raw/gini_index_madrid.csv', sep='\t')

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

gini_index['ID'] = gini_index['Distritos'].str[:7]
gini_index.drop(columns=['Distritos', 'Sections', 'Municipalities', 'Gini Index and Income Distribution P80/P20', 'Period'], inplace=True)
gini_index['ID'] = gini_index['ID'].astype('int64')

merged_2 = pd.merge(gini_index, merged, on='ID')
merged_2.rename(columns={'Total': 'Gini Index'}, inplace=True)
merged_2 = gpd.GeoDataFrame(merged_2, geometry='geometry')
merged_2 = merged_2.set_crs(gdf.crs)


# NOTE: This code fixes issues with integers and decimals, but it is a last addition and might not work. Remove if needed
#merged_2['Gini Index'] = merged_2['Gini Index'].astype(float)

# Convert the rest of the specified columns to integers
#columns_to_fix = ['Average income per consumption unit', 'Average gross income per household',
                  #'Average gross income per person', 'Average net income per household',
                  #'Average net income per person', 'Median income per consumption unit']

#for col in columns_to_fix:
#    merged_2[col] = merged_2[col].astype(str).str.replace('.', '').astype(int)

# merged.to_file("segregation_indices/data/processed/geometries_and_income.geojson", driver="GeoJSON")
merged_2.to_file("segregation_indices/data/processed/geometries_and_income.geojson", driver="GeoJSON")