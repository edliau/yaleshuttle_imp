import sqlite3
import networkx as nx
import matplotlib.pyplot as plt

# Connect to SQLite database
conn = sqlite3.connect('routedata.db')
cursor = conn.cursor()

# Create a new directed graph
G = nx.DiGraph()

# Fetch stops data from the database
cursor.execute('''SELECT id, name, latitude, longitude FROM Stops''')
stops_data = cursor.fetchall()

# Add stops as nodes to the graph
for stop_id, stop_name, latitude, longitude in stops_data:
    G.add_node(stop_id, name=stop_name, latitude=latitude, longitude=longitude)

# Fetch routes and their stops from the database
cursor.execute('''SELECT route_id, stop_id FROM RouteStops''')
route_stops_data = cursor.fetchall()

# Add directed edges between stops for each route
for route_id, stop_id in route_stops_data:
    next_stop_index = route_stops_data.index((route_id, stop_id)) + 1
    if next_stop_index < len(route_stops_data) and route_stops_data[next_stop_index][0] == route_id:
        next_stop_id = route_stops_data[next_stop_index][1]
        G.add_edge(stop_id, next_stop_id, route=route_id)

# Close connection to the database
conn.close()

# Draw the graph without arrows indicating directed edges
pos = {node: (data['longitude'], data['latitude']) for node, data in G.nodes(data=True)}
nx.draw_networkx(G, pos, with_labels=False, node_size=10, arrows=False)
plt.show()
