from flask import Flask, jsonify, request, make_response, redirect, url_for, render_template
import sqlite3
import json
from flask_cors import CORS
from collections import defaultdict
from route_finder import process_route, route_to_coords

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
    conn = sqlite3.connect(r'route_data\route_database.db')
    c = conn.cursor()

    # Get the most recent entries for each unique name
    c.execute("""
            SELECT * FROM Stops
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
    ## print(f"Stops sent")

    return jsonify(data)

@app.route('/find-shortest-route', methods=['POST'])
def find_shortest_route():
    data = request.get_json()
    start_coord = data["start"]
    end_coord = data["end"]
    route = process_route(start_coord, end_coord)
    ## print(route)
    route_coords = route_to_coords(route)
    return(jsonify(route_coords))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
