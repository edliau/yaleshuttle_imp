import sqlite3
import networkx as nx

def find_shortest_route(G, start_stop, end_stop):
    try:
        shortest_path = nx.shortest_path(G, source=start_stop, target=end_stop, weight='weight')
        return shortest_path
    except nx.NetworkXNoPath:
        return None

def process_route(input_start_stop, input_end_stop):
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

    # Find the shortest route
    shortest_route = find_shortest_route(G, input_start_stop, input_end_stop)

    processed_route = []

    if shortest_route:
        start_stop = shortest_route[0]
        next_stop = shortest_route[1]
        first_route_id = G.edges[start_stop, next_stop]['route']
        # Post-process the printed route
        processed_route.append((first_route_id, shortest_route[0]))  # Add starting stop
        for i in range(1, len(shortest_route) - 1):
            current_stop = shortest_route[i]
            previous_stop = shortest_route[i - 1]
            next_stop = shortest_route[i + 1]
            processed_route.append((G.edges[previous_stop, current_stop]['route'], current_stop))
        processed_route.append((G.edges[previous_stop, current_stop]['route'], shortest_route[-1]))  # Add final stop

    return(processed_route)