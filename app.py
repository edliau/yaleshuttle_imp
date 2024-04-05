from flask import Flask, jsonify, request, make_response, redirect, url_for, render_template
import sqlite3
import json
from flask_cors import CORS
from astar import a_star, h
from collections import defaultdict

app = Flask(__name__)
CORS(app)

@app.route('/home', methods=['GET'])
def index():
    html = render_template('index.html')
    response = make_response(html)
    return response

@app.route('/receive-coordinates', methods=['POST'])
def receive_coordinates():
    data = request.json
    start = json.loads(data["start"])
    end = json.loads(data["end"])

    return 'Coordinates received.', 200

@app.route('/data', methods=['GET'])
def get_data():
    conn = sqlite3.connect('data.db')
    c = conn.cursor()

    # Get the most recent entries for each unique name
    c.execute("""
        SELECT *
        FROM (
            SELECT *, ROW_NUMBER() OVER (PARTITION BY name ORDER BY lastUpdate DESC) AS rn
            FROM (
                SELECT *
                FROM shuttles
                ORDER BY lastUpdate DESC
                LIMIT 30
            )
        )
        WHERE rn = 1
    """)
    rows = c.fetchall()
    conn.close()

    data = []
    for row in rows:
        data.append({
            'id': row[0],
            'name': row[1],
            'lat': row[2],
            'lon': row[3],
            'heading': row[4],
            'route': row[5],
            'lastStop': row[6],
            'lastUpdate': row[7]
        })

    return jsonify(data)

@app.route('/stops', methods=['GET'])
def get_stops():
    conn = sqlite3.connect('data.db')
    c = conn.cursor()

    # Get the most recent entries for each unique name
    c.execute("""
            SELECT * FROM stops
    """)
    rows = c.fetchall()
    conn.close()

    data = []
    for row in rows:
        data.append({
            'id': row[0],
            'name': row[1],
            'lat': row[2],
            'lon': row[3],
        })

    return jsonify(data)

@app.route('/find-shortest-route', methods=['POST'])
def find_shortest_route():
    data = request.json
    start = tuple(data["start"])
    end = tuple(data["end"])

    start = round_coordinate(start, 2)
    end = round_coordinate(end, 2)

    print(start)
    print(end)

    # Define the graph with nodes spaced at intervals of 0.01 within the range of New Haven
    graph = create_graph((-74, 41), (-72, 43), 0.01)

    # Find the shortest route using A*
    shortest_route = a_star(graph, start, end)

    if shortest_route:
        # Convert the shortest route to a string format
        route_str = ' -> '.join([f'({lat},{lon})' for lat, lon in shortest_route])
        return route_str, 200
    else:
        return 'No route found.', 404

def create_graph(start, end, interval):
    graph = defaultdict(list)

    # Round off start and end coordinates to two decimal places
    start = round_coordinate(start, 2)
    end = round_coordinate(end, 2)

    # Add nodes to the graph
    current = start
    while current[0] <= end[0]:
        while current[1] <= end[1]:
            graph[current] = []
            current = round_coordinate((current[0], current[1] + interval), 2)
        current = round_coordinate((current[0] + interval, start[1]), 2)

    # Connect adjacent nodes
    for node in graph:
        x, y = node
        if (x + interval, y) in graph:
            graph[node].append((x + interval, y))  # Right
        if (x - interval, y) in graph:
            graph[node].append((x - interval, y))  # Left
        if (x, y + interval) in graph:
            graph[node].append((x, y + interval))  # Up
        if (x, y - interval) in graph:
            graph[node].append((x, y - interval))  # Down

    return graph

def round_coordinate(coord, decimals):
    x, y = coord
    return round(x, decimals), round(y, decimals)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
