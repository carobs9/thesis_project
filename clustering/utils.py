import matplotlib.colors as mcolors
import pandas as pd
import networkx as nx
import geopandas as gpd
from shapely.geometry import Polygon
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
import plotly.graph_objects as go

# DEFINING GRAPH --------------------------------------------------------------------------------------------------------- 

# Function to generate node positions based on GeoDataFrame
def get_positions(gdf):
    return {
        int(row['ID']): (row['geometry'].centroid.x, row['geometry'].centroid.y)
        for idx, row in gdf.iterrows()
    }

# Define the graph based on DataFrame
def define_graph(df, normalize_trip_count=True, remove_weak_edges=False, threshold=0.3):
    G = nx.DiGraph()

    # Group by origin and destination, and aggregate trip count and renta (taking the first renta value)
    trip_counts = df.groupby(['origen', 'destino', 'renta']).size().reset_index(name='trip_count')

    # Normalize trip counts to get weights between 0 and 1 if required
    if normalize_trip_count:
        trip_counts['weight'] = (trip_counts['trip_count'] - trip_counts['trip_count'].min()) / (trip_counts['trip_count'].max() - trip_counts['trip_count'].min())
    else:
        trip_counts['weight'] = trip_counts['trip_count']  # Use the raw trip count if not normalizing

    # NOTE: removing 'weak' edges below a threshold. This step is needed to find communities using Infomap
    if remove_weak_edges:
        trip_counts = trip_counts[trip_counts['weight'] >= threshold]

    # Add edges to the graph with 'weight' and 'renta' attributes
    for idx, row in trip_counts.iterrows():
        G.add_edge(row['origen'], row['destino'], weight=row['weight'], renta=row['renta'])  # NOTE: Save 'renta' as edge attribute

    return G, trip_counts


# PLOTTING ---------------------------------------------------------------------------------------------------------

# Set edge attributes like color and width for visualization
def set_art(G, weight_scale):
    edge_colors = []
    edge_widths = []
    
    # Iterate over the edges and set colors based on 'renta' attribute
    for u, v, data in G.edges(data=True):
        # Choose color based on 'renta' value (numerical or categorical)
        if data['renta'] == '>15':
            edge_colors.append('blue')
        elif data['renta'] == '10-15':
            edge_colors.append('red')
        else:
            edge_colors.append('green')

        # Adjust edge width based on the weight (i.e., trip count)
        edge_widths.append(max(0.5, data['weight'] / weight_scale))
    
    return edge_colors, edge_widths

def update_node_sizes(G, df, var_of_interest):
    # Create a dictionary from the income DataFrame (ID -> average_income)
    dictionary_with_ids = df.set_index('ID')[var_of_interest].to_dict()

    # Iterate over nodes and assign the 'average_income' as a node attribute (size)
    for node in G.nodes():
        if node in dictionary_with_ids:
            G.nodes[node][var_of_interest] = dictionary_with_ids[node]
        else:
            G.nodes[node][var_of_interest] = 0  # Handle missing income data
    return G

def plotly_graph(G, positions, edge_colors, edge_widths, var_of_interest, node_size_scale=0.5):
    # Extract node positions
    node_x = [positions[node][0] for node in G.nodes()]
    node_y = [positions[node][1] for node in G.nodes()]

    node_sizes = [G.nodes[node].get(var_of_interest, 0) for node in G.nodes()]
    scaled_node_sizes = [size * node_size_scale for size in node_sizes]

    # Create node scatter trace
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        marker=dict(size=scaled_node_sizes, color='white', line=dict(width=2, color='#888')),
        text=[f'Node {node}' for node in G.nodes()],
        hoverinfo='text'
    )

    # Prepare edges in batches based on edge color (blue, red, green)
    edge_traces = []
    for edge_color in ['blue', 'green', 'red']:
        edge_x, edge_y = [], []
        for i, (u, v, data) in enumerate(G.edges(data=True)):
            if edge_colors[i] == edge_color:
                x0, y0 = positions[u]
                x1, y1 = positions[v]
                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])

        # Create edge trace for each color
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

    # Combine edge and node traces
    fig = go.Figure(data=edge_traces + [node_trace], layout=layout)
    fig.show()

# ANALYSIS ---------------------------------------------------------------------------------------------------------

def check_in_weights(G):
    in_weights = {}
    for node in G.nodes():
        total_in_weight = sum(data['weight'] for u, v, data in G.in_edges(node, data=True))
        in_weights[node] = total_in_weight
        print(f"Node {node} Total In-weight: {total_in_weight}")
    return in_weights

def check_out_weights(G):
    out_weights = {}
    for node in G.nodes():
        total_out_weight = sum(data['weight'] for u, v, data in G.out_edges(node, data=True))
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

def plot_communities(G, positions, communities, edge_colors, edge_widths, var_of_interest, node_size_scale=0.5):
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
    for edge_color in ['blue', 'green', 'red']:
        edge_x, edge_y = [], []
        for i, (u, v, data) in enumerate(G.edges(data=True)):
            if edge_colors[i] == edge_color:
                x0, y0 = positions[u]
                x1, y1 = positions[v]
                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])

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