import matplotlib.colors as mcolors
import pandas as pd
import networkx as nx
import geopandas as gpd
from shapely.geometry import Polygon
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
import plotly.graph_objects as go
import numpy as np

# DEFINING LABELS OF NODES 
district_mapping = pd.read_csv('/Users/caro/Desktop/thesis_project/data_overview/outputs/districts_and_population.csv')
id_to_name = district_mapping.set_index('ID')['name_2'].to_dict()

# DEFINING GRAPH --------------------------------------------------------------------------------------------------------- 

# Function to generate node positions based on GeoDataFrame
def get_positions(gdf):
    return {
        int(row['ID']): (row['geometry'].centroid.x, row['geometry'].centroid.y) 
        for idx, row in gdf.iterrows()
    }

# Define graph based on OD trips including normalisation by population 
def define_graph(trip_counts, remove_weak_edges=False, threshold=0.1, standardise=False):
    """
    Define a directed graph from a DataFrame with trip counts and optional population normalization.

    Parameters:
    - df: DataFrame containing 'origen', 'destino', and trip data.
    - population_df: DataFrame containing district population with 'district' and 'population' columns.
    - NORMALISE_BY_POP: Boolean, if True, normalizes trip counts by the population of the origin district.
    - remove_weak_edges: Boolean, if True, removes edges with normalized weight below the threshold.
    - threshold: Float, the minimum normalized weight to include an edge.

    Returns:
    - G: A directed graph (networkx.DiGraph).
    - trip_counts: DataFrame with trip count and normalized trip count.
    """
    G = nx.DiGraph()
    
    # Normalize trip counts between 0 and 1
    if standardise:
        trip_counts['normalized_trip_count'] = (
            (trip_counts['normalized_trip_count'] - trip_counts['normalized_trip_count'].min()) /
            (trip_counts['normalized_trip_count'].max() - trip_counts['normalized_trip_count'].min()))

    # Option to remove weak edges below a threshold
    if remove_weak_edges:
        trip_counts = trip_counts[trip_counts['normalized_trip_count'] >= threshold]

    # Add edges to the graph with correct attributes
    for idx, row in trip_counts.iterrows():
        G.add_edge(
            row['origen'], 
            row['destino'], 
            weight=row['normalized_trip_count']
        )
    
    return G


# PLOTTING ---------------------------------------------------------------------------------------------------------

# Set edge attributes like color and width for visualization. NOTE: Color has been removed for ease of analysis
def set_art(G, weight_scale):
    edge_widths = []
    
    # Iterate over the edges and set widths based on the 'weight' attribute
    for u, v, data in G.edges(data=True):
        # Scale the weight to get appropriate edge widths
        width = data['weight'] / weight_scale
        edge_widths.append(max(0.5, width))  # Ensuring a minimum width of 0.5
    
    return edge_widths

def update_node_sizes(G, df, var_of_interest):
    # Create a dictionary from the income DataFrame (ID -> average_income)
    dictionary_with_ids = df.set_index('ID')[var_of_interest].to_dict()

    # Iterate over nodes and assign the income as a node attribute (size)
    for node in G.nodes():
        if node in dictionary_with_ids:
            G.nodes[node][var_of_interest] = dictionary_with_ids[node]
        else:
            G.nodes[node][var_of_interest] = 0  # Handle missing income data
    return G

def plotly_graph(G, positions, edge_widths, var_of_interest, node_size_scale=0.05):
    # Extract node positions
    node_x = [positions[node][0] for node in G.nodes()]
    node_y = [positions[node][1] for node in G.nodes()]

    # Extract node sizes (scaled by the provided scale)
    node_sizes = [G.nodes[node].get(var_of_interest, 0) for node in G.nodes()]
    scaled_node_sizes = [size * node_size_scale for size in node_sizes]

    # Create the node scatter trace
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        marker=dict(size=scaled_node_sizes, color='white', line=dict(width=2, color='#888')),
        text=[f'District: {id_to_name.get(node, "Unknown")}' for node in G.nodes()],
        hoverinfo='text',
        showlegend=False 
    )

    # Prepare edge traces
    edge_traces = []
    cmap = plt.cm.get_cmap('RdYlBu_r')
    edge_weights = [data['weight'] for _, _, data in G.edges(data=True)]

    # Normalize weights between 0 and 1
    weights_normalized = np.array(edge_weights)

    for i, (u, v, data) in enumerate(G.edges(data=True)):
        edge_x, edge_y = [], []
        x0, y0 = positions[u]
        x1, y1 = positions[v]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

        color = cmap(data['weight'])  # Get color from colormap based on the normalized weight
        color = f'rgba({color[0]*255}, {color[1]*255}, {color[2]*255}, {color[3]})'

        # Create a single edge trace with the specified color and individual width
        edge_traces.append(
            go.Scatter(
                x=edge_x, y=edge_y,
                line=dict(width=edge_widths[i], color=color),
                text=f"Width: {edge_widths[i]:.2f}", 
                hoverinfo='text',
                mode='lines',
                showlegend=False 
            )
        )

    

        # Create a scatter trace that adds the colorbar (color scale) for edges
    colorbar_trace = go.Scatter(
        x=[None], y=[None],  # Invisible points
        mode='markers',
        marker=dict(
            colorscale='RdYlBu_r',  # Matching the colormap
            cmin=min(weights_normalized),  # Min of weights
            cmax=max(weights_normalized),  # Max of weights
            colorbar=dict(
                title="Edge Weight",  # Title for colorbar
                tickvals=np.linspace(min(weights_normalized), max(weights_normalized), 5),  # Ticks on colorbar
                ticktext=[f"{v:.2f}" for v in np.linspace(min(weights_normalized), max(weights_normalized), 5)],  # Text for ticks
            ),
            showscale=True  # Show colorbar
        ),
        hoverinfo='none'
    )

    # Create layout for the graph
    layout = go.Layout(
        showlegend=True,
        hovermode='closest',
        margin=dict(b=0, l=0, r=0, t=0),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
    )

    # Combine edge and node traces
    fig = go.Figure(data=edge_traces + [node_trace, colorbar_trace], layout=layout)
    return fig

# ANALYSIS ---------------------------------------------------------------------------------------------------------

def check_in_weights(G):
    in_weights = {}
    for node in G.nodes():
        total_in_weight = round(sum(data['weight'] for u, v, data in G.in_edges(node, data=True)), 2)
        in_weights[node] = total_in_weight
        print(f"Node {node} Total In-weight: {total_in_weight}")
    return in_weights

def check_out_weights(G):
    out_weights = {}
    for node in G.nodes():
        total_out_weight = round(sum(data['weight'] for u, v, data in G.out_edges(node, data=True) if u != v  # Exclude self-loops
        ),2)
        out_weights[node] = total_out_weight
        print(f"Node {node} Total Out-weight: {total_out_weight}")
    return out_weights

def print_node_degrees(G):
    print("Node Degrees (In-degree, Out-degree, Total degree):")
    for node in G.nodes():
        in_degree = G.in_degree(node)
        out_degree = G.out_degree(node)
        total_degree = G.degree(node)  # Total degree (in + out)
        print(f"Node {node}: In-degree = {in_degree}, Out-degree = {out_degree}, Total degree = {total_degree}")

def get_adj_matrix(G):
    nodes = list(G.nodes)
    adj = pd.DataFrame(nx.adjacency_matrix(G, weight='weight').toarray(), index=nodes, columns=nodes)
    return adj


# PLOT COMMUNITIES ---------------------------------------------------------------------------------------------------

def plot_communities(G, positions, communities, edge_widths, var_of_interest, edge_color="#888", node_size_scale=0.05):
    # Get a list of unique colors for each community using matplotlib
    colors = list(mcolors.CSS4_COLORS.keys())[:len(communities)]

    # Create a mapping of nodes to their respective community
    node_community_map = {}
    for community_index, community in enumerate(communities):
        for node in community:
            node_community_map[node] = community_index

    # Extract node positions
    node_x = [positions[node][0] for node in G.nodes()]
    node_y = [positions[node][1] for node in G.nodes()]

    # Create node scatter trace with community-based colors
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        marker=dict(
            size=[G.nodes[node].get(var_of_interest, 0) * node_size_scale for node in G.nodes()],
            color=[colors[node_community_map[node]] for node in G.nodes()],
            line=dict(width=2, color='#888')
        ),
        text=[f'Node {node}' for node in G.nodes()],
        hoverinfo='text'
    )

    # Prepare edges
    edge_traces = []
    for i, (u, v, data) in enumerate(G.edges(data=True)):
        edge_x, edge_y = [], []
        x0, y0 = positions[u]
        x1, y1 = positions[v]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

        # Create a single edge trace with the specified color and individual width
        edge_traces.append(
            go.Scatter(
                x=edge_x, y=edge_y,
                line=dict(width=edge_widths[i], color=edge_color),
                hoverinfo='none',
                mode='lines'
            )
        )
    # Create a layout for the graph
    layout = go.Layout(
        showlegend=True,
        legend=dict(
            x=1,  
            y=0,  
            xanchor='right',  
            yanchor='bottom', 
        ),
        hovermode='closest',
        margin=dict(b=0, l=0, r=0, t=0),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
    )

    # Combine edge and node traces and plot
    fig = go.Figure(data=edge_traces + [node_trace], layout=layout)
    return fig
    #fig.show()
