import sqlite3
import networkx as nx
from math import radians, sin, cos, sqrt, atan2
from collections import deque

def find_shortest_route(G, start_stop, end_stop):
    try:
        shortest_path = nx.shortest_path(G, source=start_stop, target=end_stop, weight='weight')
        return shortest_path
    except nx.NetworkXNoPath:
        return None

# Function to calculate the distance between two points using the Haversine formula
def haversine_distance(lat1, lon1, lat2, lon2):
    # Convert latitude and longitude from degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = 6371 * c  # Radius of Earth in kilometers
    return distance

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
            # Calculate weight based on Haversine distance between stops
            current_stop_data = cursor.execute('''SELECT latitude, longitude FROM Stops WHERE id = ?''', (stop_id,)).fetchone()
            next_stop_data = cursor.execute('''SELECT latitude, longitude FROM Stops WHERE id = ?''', (next_stop_id,)).fetchone()
            if current_stop_data and next_stop_data:
                current_lat, current_lon = current_stop_data
                next_lat, next_lon = next_stop_data
                distance = haversine_distance(current_lat, current_lon, next_lat, next_lon)
                G.add_edge(stop_id, next_stop_id, route=route_id, weight=distance)


    # Find the shortest route
    shortest_route = find_shortest_route(G, input_start_stop, input_end_stop)

    processed_route = []

    if shortest_route:
        if len(shortest_route) == 2:  # If the shortest route contains only one stop
            # Calculate the distance directly between start and end stops
            cursor.execute('''SELECT latitude, longitude FROM Stops WHERE id = ?''', (input_start_stop,))
            start_stop_data = cursor.fetchone()
            cursor.execute('''SELECT latitude, longitude FROM Stops WHERE id = ?''', (input_end_stop,))
            end_stop_data = cursor.fetchone()
            start_stop = shortest_route[0]
            next_stop = shortest_route[1]
            first_route_id = G.edges[start_stop, next_stop]['route']
            if start_stop_data and end_stop_data:
                start_lat, start_lon = start_stop_data
                end_lat, end_lon = end_stop_data
                distance = haversine_distance(start_lat, start_lon, end_lat, end_lon)
                processed_route.append((first_route_id, input_start_stop, distance))
        else:
            total_distance = 0
            start_stop = shortest_route[0]
            next_stop = shortest_route[1]
            first_route_id = G.edges[start_stop, next_stop]['route']
            total_distance += G.edges[start_stop, next_stop]['weight']
            # Post-process the printed route
            processed_route.append((first_route_id, shortest_route[0], total_distance))  # Add starting stop
            for i in range(1, len(shortest_route) - 1):
                current_stop = shortest_route[i]
                previous_stop = shortest_route[i - 1]
                next_stop = shortest_route[i + 1]
                segment_distance = G.edges[previous_stop, current_stop]['weight']
                total_distance += segment_distance
                processed_route.append((G.edges[previous_stop, current_stop]['route'], current_stop, segment_distance))
            segment_distance = G.edges[previous_stop, current_stop]['weight']
            total_distance += segment_distance
            processed_route.append((G.edges[previous_stop, current_stop]['route'], shortest_route[-1], segment_distance))  # Add final stop

     # Close connection to the database
    conn.close()

    return(processed_route)

def find_best_route(start_coords, end_coords):
    bus_stop_distances = []
    conn = sqlite3.connect('route_data/route_database.db')
    cursor = conn.cursor()

    # Fetch all stops from the database
    cursor.execute('''SELECT id, name, latitude, longitude FROM Stops''')
    stops_data = cursor.fetchall()

    # Fetch stop IDs from the RouteStops table
    cursor.execute('''SELECT DISTINCT stop_id FROM RouteStops''')
    route_stops = set(row[0] for row in cursor.fetchall())

    conn.close()

    # Calculate distances from start and end coordinates to each stop
    for stop_id, stop_name, lat, lon in stops_data:
        if stop_id in route_stops:
            distance_to_start = haversine_distance(start_coords[0], start_coords[1], lat, lon)
            distance_to_end = haversine_distance(end_coords[0], end_coords[1], lat, lon)
            bus_stop_distances.append((stop_id, stop_name, distance_to_start, distance_to_end))

    # Sort bus stops by total distance
    bus_stop_distances_from_start = sorted(bus_stop_distances, key=lambda x: x[2])
    #get closest 15 bus stops to start
    closest_stops = bus_stop_distances_from_start[:15]
    #find the bus_stop closest to the selected end coordinates
    bus_stop_distances_from_end = sorted(bus_stop_distances, key=lambda x: x[3])
    target_final_stop = bus_stop_distances_from_end[0]

    distance_scores = []

    for stop in closest_stops:
        route = process_route(stop[0], target_final_stop[0])
        if route:
            total_distance = sum(segment[2] for segment in route)  # Extract total distance from the processed route
            distance_scores.append((stop[0],stop[1],total_distance))

    for starting_stop in bus_stop_distances_from_start:
        for index, stop in enumerate(distance_scores):
            if starting_stop[0] == stop[0]:
                # If stop_id matches, update the tuple in distance_scores to include distance_to_start
                distance_scores[index] = (stop[0], stop[1], stop[2], starting_stop[2])

    weighted_scores = []
    for stop_id, stop_name, bus_distance, distance_to_start in distance_scores:
        weighted_score = 0.3 * bus_distance + 0.7 * distance_to_start
        weighted_scores.append((stop_id, stop_name, weighted_score))
    shortest_route_stop = min(weighted_scores, key=lambda x: x[2])
    
    return process_route(shortest_route_stop[0],target_final_stop[0])

def route_to_coords(route):
    conn = sqlite3.connect('route_data/route_database.db')
    cursor = conn.cursor()
    coords = []
    for route_id, stop_id in route:
        print(stop_id)
        cursor.execute('''SELECT latitude, longitude FROM Stops WHERE id = ?''', (stop_id,))
        lat, lon = cursor.fetchone()
        coords.append([(lon, lat), route_id])
    conn.close()
    return coords