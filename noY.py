import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict
#import matplotlib.patches as patches
#import matplotlib.colors as mcolors
import matplotlib.cm as cm

df = pd.read_csv('noYears.csv')

connections = defaultdict(set)
node_depths = defaultdict(int)

# Iterate over the file paths in the CSV
for path in df['Path'].unique():
    # Split the path into folders (nodes)
    nodes = path.split('/')
    # Update connections and depths for each node
    for i, node in enumerate(nodes):
        if i < len(nodes) - 1:
            connections[node].add(nodes[i+1])
        else:
            # Ensure the last node is also in the connections dictionary
            if node not in connections:
                connections[node] = set()
        # Update the depth of each node
        node_depths[node] = max(node_depths[node], i)

# Prepare data for the new CSV
data = {'Node Name': [], 'Connection Number': [], 'Connection Names': [], 'Node Depths': []}
for node, node_connections in connections.items():
    data['Node Name'].append(node)
    data['Connection Number'].append(len(node_connections))
    data['Connection Names'].append('@ '.join(node_connections))
    data['Node Depths'].append(node_depths[node])

# Create a DataFrame from the data
connections_df = pd.DataFrame(data)
connections_df.sort_values(by='Connection Number', ascending=False, inplace=True)

# Write the DataFrame to a new CSV file
connections_df.to_csv('noYconnections.csv', index=False)

# Load the CSV file
connections_df = pd.read_csv('noYconnections.csv')

# Create a directed graph
G = nx.DiGraph()

# Add nodes and edges to the graph
for _, row in connections_df.iterrows():
    node = row['Node Name']
    connections = row['Connection Names']
    if isinstance(connections, str) and connections:  # Check if 'Connection Names' is a non-empty string
        if '@ ' in connections:
            connections_list = connections.split('@ ')
        else:
            connections_list = [connections]  # Single connection, no split needed
        for connection in connections_list:
            G.add_edge(node, connection)
node_sizes = [G.degree(node) * 5 for node in G.nodes]


# Define the number of unique depth levels
unique_depths = sorted(set(node_depths.values()))
num_depths = len(unique_depths)

# Use the 'viridis' colormap
viridis = cm.get_cmap('viridis', num_depths)

# Map each depth level to a color in 'viridis'
depth_colors = {depth: viridis(i / (num_depths - 1)) for i, depth in enumerate(unique_depths)}

# Map node depth to color
node_colors = [depth_colors.get(node_depths[node], (0.5, 0.5, 0.5, 1.0)) for node in G.nodes]


# Draw the graph
pos = nx.spring_layout(G)  
nx.draw(G, pos, style='dotted',
        edge_color='lightgray', 
        with_labels=False, 
        node_size=node_sizes, 
        node_color=node_colors,
        arrows=True, alpha=0.4)
# Create a legend
# Define categories for the legend
handles = [plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=viridis(i / (num_depths - 1)),
                      markersize=10, label=f'Depth {depth}') for i, depth in enumerate(unique_depths)]
plt.legend(handles=handles, title='Node Depth')


# Identify top 5 nodes with the most connections
top_nodes = connections_df.head(30)['Node Name'].tolist()
nx.draw_networkx_labels(G, pos, labels={node: node for node in top_nodes}, font_size=2, bbox=dict(facecolor='white', alpha=0.5), horizontalalignment='center')

# Show plot
plt.title('Folder Relationships')
plt.show()
