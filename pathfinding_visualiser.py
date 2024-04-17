import sqlite3
import networkx as nx

# Function to find the shortest route between two stops
def find_shortest_route(G, start_stop, end_stop):
    try:
        shortest_path = nx.shortest_path(G, source=start_stop, target=end_stop, weight='weight')
        return shortest_path
    except nx.NetworkXNoPath:
        return None

import sqlite3
import networkx as nx

# Connect to SQLite database
conn = sqlite3.connect('route_data/route_database.db')
cursor = conn.cursor()

# Create a new directed graph
G = nx.DiGraph()

# Maintain a set to store unique stop IDs
unique_stops = set()

# Fetch routes and their stops from the database
cursor.execute('''SELECT route_id, stop_id FROM RouteStops''')
route_stops_data = cursor.fetchall()

# Add stops as nodes to the graph only if they correspond to route values
for route_id, stop_id in route_stops_data:
    # Check if the stop ID is already encountered
    if stop_id not in unique_stops:
        cursor.execute('''SELECT id, name, latitude, longitude FROM Stops WHERE id = ?''', (stop_id,))
        stop_data = cursor.fetchone()
        if stop_data:
            stop_id, stop_name, latitude, longitude = stop_data
            G.add_node(stop_id, id=stop_id, name=stop_name, latitude=latitude, longitude=longitude)
            # Add the stop ID to the set of unique stops
            unique_stops.add(stop_id)

# Add directed edges between stops for each route
for route_id, stop_id in route_stops_data:
    next_stop_index = route_stops_data.index((route_id, stop_id)) + 1
    if next_stop_index < len(route_stops_data):
        next_stop_id = route_stops_data[next_stop_index][1]
        # Calculate weight based on distance between stops (you can use other metrics if available)
        weight = 1  # Placeholder weight, you can replace this with actual distance calculation
        G.add_edge(stop_id, next_stop_id, route=route_id, weight=weight)

# Close connection to the database
conn.close()

# Input start and end stops
start_stop = input("Enter the ID of the start stop: ")
end_stop = input("Enter the ID of the end stop: ")

start_stop = int(start_stop)
end_stop = int(end_stop)

# Find the shortest route
shortest_route = find_shortest_route(G, start_stop, end_stop)

if shortest_route:
    # Post-process the printed route
    processed_route = [(0,shortest_route[0])]  # Add starting stop
    for i in range(1, len(shortest_route) - 1):
        current_stop = shortest_route[i]
        previous_stop = shortest_route[i - 1]
        next_stop = shortest_route[i + 1]
        processed_route.append((G.edges[current_stop, next_stop]['route'], current_stop))
    processed_route.append((G.edges[previous_stop, current_stop]['route'], shortest_route[-1]))  # Add final stop
    print("Processed route:")
    for route_stop_pair in processed_route:
        if route_stop_pair:  # Skip empty tuples
            print(route_stop_pair)
else:
    print("No route found between the given stops.")

import matplotlib.pyplot as plt

# Function to draw the graph
def draw_graph(G):
    pos = nx.get_node_attributes(G, 'pos')
    labels = nx.get_node_attributes(G, 'id')

    # Default node colors
    node_color_map = ['skyblue' if node not in shortest_route else 'green' for node in G]

    # Draw the network
    nx.draw(G, pos, labels=labels, with_labels=True, node_size=20, node_color=node_color_map, font_size=3)

    # Draw edge labels to show the weights
    #edge_labels = nx.get_edge_attributes(G, 'weight')
    #nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red')

    #without weights visualised for now:
    #nx.draw_networkx_edges(G, pos, alpha=0.5, edge_color='gray')

    # Show the plot
    plt.show()

# Assuming you have latitude and longitude as attributes,
# you need to set them as positions for the nodes
for node in G.nodes(data=True):
    G.nodes[node[0]]['pos'] = (node[1]['longitude'], node[1]['latitude'])

draw_graph(G)


