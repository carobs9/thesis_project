import config as cfg
import os
import pandas as pd
# from utils import get_overview, open_gz, filter_district  
import networkx as nx
import matplotlib.pyplot as plt
from shapely.geometry import Polygon
import geopandas as gpd
from sklearn.model_selection import train_test_split

# Load Data
def load_data():
    """Load and preprocess necessary data."""
    try:
        all_viajes = pd.read_csv('mobility_data/viajes/all_viajes_week_0222.csv')
        gdf = gpd.read_file(cfg.ZONIFICACION_DATA / 'distritos/madrid_gdf.geojson')
        gdf = gdf.to_crs(epsg=3042)
        return all_viajes, gdf
    except Exception as e:
        print(f"Error loading data: {e}")
        return None, None

# Get Positions
def get_positions(gdf):
    """Generate a dictionary of positions based on GeoDataFrame centroids."""
    positions = {int(row['ID']): (row['geometry'].centroid.x, row['geometry'].centroid.y) 
                 for idx, row in gdf.iterrows()}
    return positions

# Define Graph
def define_graph(df, weight_column='viajes', filters=None):
    """Create a NetworkX graph based on the filtered DataFrame."""
    if filters is None:
        filters = {
            'attr1': {'column': 'renta', 'value': '>15'},
            'attr2': {'column': 'renta', 'value': '10-15'}
        }
    
    G = nx.DiGraph()
    
    # Apply filters to add edges with attributes
    for attr, criteria in filters.items():
        subset = df[df[criteria['column']] == criteria['value']]
        for idx, row in subset.iterrows():
            G.add_edge(row['origen'], row['destino'], weight=row[weight_column], type=attr)
    
    return G

# Set Edge Styles
def set_art(G):
    """Create edge styles based on the graph's attributes."""
    edge_colors = []
    edge_widths = []
    for u, v, data in G.edges(data=True):
        # Set edge color based on the type
        edge_colors.append('blue' if data['type'] == 'attr1' else 'red')
        # Set edge width based on the number of trips (weight)
        edge_widths.append(max(0.5, data['weight'] / 15))  # Scale down weight for visualization purposes
    return edge_colors, edge_widths

# Plot Graph and Background
def plot_graph_and_background(G, pos, edge_colors, edge_widths, node_size=500, 
                              node_color='white', background=None, alpha=0.3):
    """Plot graph with a background map."""
    fig, ax = plt.subplots(figsize=(10, 15))

    # Plot the background if it's a GeoDataFrame
    if isinstance(background, gpd.GeoDataFrame):
        background.plot(ax=ax, color='lightgrey', edgecolor='black', alpha=alpha)

    # Ensure edge attributes are consistent in length
    assert len(edge_colors) == len(edge_widths) == len(G.edges()), "Mismatch in lengths of edge attributes."

    # Draw the graph
    nx.draw(G, pos=pos, with_labels=True, edge_color=edge_colors, width=edge_widths, 
            node_size=node_size, node_color=node_color, ax=ax)
    plt.title('Graph with Background Map')
    plt.show()

# Main Function
def main():
    # Load data
    all_viajes, gdf = load_data()
    if all_viajes is None or gdf is None:
        print("Failed to load data.")
        return

    # Filter data
    filtered_df = all_viajes[all_viajes['actividad_origen'] == 'casa']

    # Generate positions
    positions = get_positions(gdf)

    # Define graph
    G = define_graph(filtered_df, weight_column='viajes')

    # Get edge styles
    edge_colors, edge_widths = set_art(G)

    # Plot the graph with the background
    plot_graph_and_background(G, positions, edge_colors, edge_widths, 500, 'white', gdf, 0.3)

# Entry point
if __name__ == "__main__":
    main()
