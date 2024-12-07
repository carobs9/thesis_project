import config as cfg
from utils import *
import seaborn as sns
import numpy as np
import pickle

all_viajes = pd.read_csv('/Users/caro/Desktop/thesis_project/mobility_data/VIAJES/viajes_week_0322.csv',thousands='.',decimal=',')
income = gpd.read_file('/Users/caro/Desktop/thesis_project/segregation_indices/data/processed/geometries_and_income.geojson')
gdf = gpd.read_file(cfg.ZONIFICACION_DATA / 'distritos/madrid_gdf.geojson')  
gdf = gdf.to_crs(epsg=4326) 

filtered_df = all_viajes.loc[(all_viajes['actividad_origen'] == 'casa')]
income['Gini Index Scaled'] = income['Gini Index'] ** 2.5

var_of_interest = 'Median income per consumption unit' # or 'Gini Index Scaled'

district_counts = filtered_df['origen'].value_counts().reset_index()
district_counts.columns = ['ID', 'Population']

G, trip_counts = define_graph(filtered_df, district_counts, NORMALISE_BY_POP=True, remove_weak_edges=False, threshold=0.2)
G = update_node_sizes(G, income, var_of_interest)

id_to_name = district_mapping.set_index('ID')['name_2'].to_dict()
G = nx.relabel_nodes(G, id_to_name)

adj_matrix = nx.adjacency_matrix(G, weight='weight').toarray()

# saving graph and adj matrix
# pickle.dump(G, open('graphs/normalized_march_22_home_origin.pickle', 'wb'))
# np.save('adjacency_matrices/normalized_filtered_df.npy', adj_matrix)