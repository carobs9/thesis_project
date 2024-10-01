import config as cfg
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import geopandas as gpd
import matplotlib.pyplot as plt

all_viajes = pd.read_csv('viajes/all_viajes_month_0322.csv')
gdf = gpd.read_file(cfg.ZONIFICACION_DATA / 'distritos/madrid_gdf.geojson')  # Load your GeoJSON file into a GeoDataFrame
gdf = gdf.to_crs(epsg=3042)

filtered_df = all_viajes.loc[(all_viajes['actividad_origen'] == 'casa')]

def get_positions(gdf):
    positions = {}
    for idx, row in gdf.iterrows():
        district_id = row['ID']  # Assuming 'ID' is the district identifier matching the graph
        centroid = row['geometry'].centroid  # Get the centroid of the district's polygon
        positions[district_id] = (centroid.x, centroid.y)  # Store the centroid coordinates

    positions = {int(key): value for key, value in positions.items()}
    return positions

def define_graph(df, weight_column): # FIXME: Make it prettier to choose weight and var of interest
    # filters to plot -- the edge color will change based on these filters
    attr1 = df[df['renta'] == '>15']
    attr2 = df[df['renta'] == '10-15']

    G = nx.DiGraph() 
    # add edges with attribute 1
    for idx, row in attr1.iterrows():
        G.add_edge(row['origen'], row['destino'], weight=row[weight_column], type='attr1')

    # add edges with attribute 2
    for idx, row in attr2.iterrows():
        G.add_edge(row['origen'], row['destino'], weight=row[weight_column], type='attr2')

    return G

def set_art(G):
    edge_colors = []
    edge_widths = []
    for u, v, data in G.edges(data=True):
        # Set edge color based on the type
        if data['type'] == 'attr1':
            edge_colors.append('blue')  # attr1 edges will be blue
        else:
            edge_colors.append('red')   # attr2 edges will be red

        # Set edge width based on the number of trips (weight), avoid too small widths
        edge_widths.append(max(0.5, data['weight'] / 15))  # Scale down weight for visualization purposes

    return edge_colors, edge_widths

def plot_graph_and_background(G, pos, edge_colors, edge_widths, node_size, node_color, background, alpha):
    fig, ax = plt.subplots(figsize=(10, 15))
    # Plot the background if it is a GeoDataFrame
    if hasattr(background, 'plot'):
        background.plot(ax=ax, color='green', edgecolor='green', alpha=alpha)
    # Check that edge attributes match number of edges in G
    assert len(edge_colors) == len(edge_widths) == len(G.edges()), "Mismatch in lengths of edge attributes."
    # Draw the graph
    nx.draw(G, pos=pos, with_labels=True, edge_color=edge_colors, width=edge_widths, 
            node_size=node_size, node_color=node_color, ax=ax)

    plt.show()

positions = get_positions(gdf)
G = define_graph(filtered_df, 'viajes')
edge_colors, edge_widths = set_art(G)
plot_graph_and_background(G, positions, edge_colors, edge_widths, 500, 'white', gdf, 0.3)

nx.write_gml(G, "0322_graph.gml")