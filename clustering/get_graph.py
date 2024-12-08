import config as cfg
from utils import *
import seaborn as sns
import numpy as np
import pickle

if cfg.type_of_study == 'month':
    file_name = 'all_viajes_month_0322.csv'
elif cfg.type_of_study == 'week':
    file_name = 'viajes_week_0322.csv'  #TODO: CORRECT IF NEEDED
elif cfg.type_of_study == 'two_weeks':
    file_name = 'viajes_two_weeks_0322.csv'  #TODO: CORRECT IF NEEDED
else:
    file_name = 'default_file.csv'  # FIXME: Fallback option if neither is True

all_viajes = pd.read_csv(cfg.MOBILITY_DATA / f'VIAJES/{file_name}', thousands='.', decimal=',') #df of interest
filtered_df = all_viajes.loc[(all_viajes['actividad_origen'] == 'casa')]

income = gpd.read_file('/Users/caro/Desktop/thesis_project/segregation_indices/data/processed/geometries_and_income.geojson')
trip_counts = pd.read_csv(f'/Users/caro/Desktop/thesis_project/trip_analysis/outputs/{cfg.type_of_study}_normalized_trip_count.csv')
gdf = gpd.read_file(cfg.ZONIFICACION_DATA / 'distritos/madrid_gdf.geojson')  
gdf = gdf.to_crs(epsg=4326) 

income['Gini Index Scaled'] = income['Gini Index'] ** 2.5

var_of_interest = 'Median income per consumption unit' # or 'Gini Index Scaled'

district_counts = filtered_df.groupby('origen')['viajes'].sum().reset_index(name='total_viajes') # FIXED
district_counts.columns = ['ID', 'Population']

G = define_graph(trip_counts, remove_weak_edges=False, threshold=0.2, standardise=True)
G = update_node_sizes(G, income, var_of_interest)

id_to_name = district_mapping.set_index('ID')['name_2'].to_dict()
G = nx.relabel_nodes(G, id_to_name)

adj_matrix = nx.adjacency_matrix(G, weight='weight').toarray()

plt.figure(figsize=(10, 8))
sns.heatmap(
    get_adj_matrix(G), 
    annot=True, 
    cmap='viridis', 
    cbar_kws={'label': 'Weights'}, 
    fmt=".1f"
)
plt.title(f'Trips - {cfg.type_of_study}')
plt.xlabel('Destination District')
plt.ylabel('Home District');
plt.tight_layout()
plt.savefig(f'/Users/caro/Desktop/thesis_project/clustering/figures/{file_name}_adjacency_heatmap.png', dpi=300, bbox_inches='tight')

# saving graph and adj matrix
pickle.dump(G, open(f'/Users/caro/Desktop/thesis_project/clustering/graphs/{file_name}.pickle', 'wb'))
np.save(f'/Users/caro/Desktop/thesis_project/clustering/adjacency_matrices/{file_name}.npy', adj_matrix)

print('Done!')
