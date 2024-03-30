import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt

# Define the address
address = "Yale University"

# Define tags for bus stops and bus routes
bus_stops_tags = {
    "network": "Yale Shuttle",
    "highway": "bus_stop"
}

bus_routes_tags ={
    "network": "Yale Shuttle",
    "route": "bus"
}

# Retrieve bus stops and bus routes near the address
stops = ox.geometries_from_address(address, tags=bus_stops_tags, dist=10000)
routes = ox.geometries_from_address(address, tags=bus_routes_tags, dist=10000)

# Create a new NetworkX graph
G = nx.Graph()

# Add bus stop POIs as nodes to the graph
for idx, poi in stops.iterrows():
    G.add_node(idx, pos=(poi.geometry.x, poi.geometry.y))

# Add edges between bus stops based on bus routes
for idx, route in routes.iterrows():
    # Extract the bus stops along the route
    bus_stops = route.geometry.coords
    # Iterate over consecutive pairs of bus stops
    for u, v in zip(bus_stops[:-1], bus_stops[1:]):
        # Find the indices of the bus stops in the stops dataframe
        u_idx = stops.index[(stops.geometry.x == u[0]) & (stops.geometry.y == u[1])].tolist()[0]
        v_idx = stops.index[(stops.geometry.x == v[0]) & (stops.geometry.y == v[1])].tolist()[0]
        # Add an edge between the consecutive bus stops in the graph
        print("Adding edge between nodes:", u_idx, "-", v_idx)
        G.add_edge(u_idx, v_idx)

# Set a CRS for the graph (optional)
G.graph["crs"] = stops.crs

# Visualize the graph with nodes and edges
pos = nx.get_node_attributes(G, "pos")
nx.draw(G, pos, node_size=20, node_color="blue", with_labels=False, edge_color="gray", alpha=0.5)
plt.show()
