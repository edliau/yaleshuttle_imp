import requests
import sqlite3

# Fetch JSON data for routes and stops
routes_url = "https://yale.downtownerapp.com/routes_routes.php?inactive=true"
stops_url = "https://yale.downtownerapp.com/routes_stops.php"
routes_response = requests.get(routes_url)
stops_response = requests.get(stops_url)
routes_data = routes_response.json()
stops_data = stops_response.json()

# Connect to SQLite database
conn = sqlite3.connect('route_database.db')
cursor = conn.cursor()

# Create tables if they don't exist
cursor.execute('''CREATE TABLE IF NOT EXISTS Routes (
                    id INT PRIMARY KEY,
                    name VARCHAR(255),
                    short_name VARCHAR(50),
                    description VARCHAR(255),
                    color VARCHAR(10),
                    active BOOLEAN
                )''')

cursor.execute('''CREATE TABLE IF NOT EXISTS Stops (
                    id INT PRIMARY KEY,
                    name VARCHAR(255),
                    latitude FLOAT,
                    longitude FLOAT
                )''')

cursor.execute('''CREATE TABLE IF NOT EXISTS RouteStops (
                    route_id INT,
                    stop_id INT,
                    FOREIGN KEY (route_id) REFERENCES Routes(id),
                    FOREIGN KEY (stop_id) REFERENCES Stops(id)
                )''')

# Insert data into Stops table
for stop in stops_data:
    stop_id = stop['id']
    stop_name = stop['name']
    latitude = stop['lat']
    longitude = stop['lon']

    cursor.execute('''INSERT INTO Stops (id, name, latitude, longitude)
                      VALUES (?, ?, ?, ?)''', (stop_id, stop_name, latitude, longitude))

# Insert data into Routes table and RouteStops table
for route in routes_data:
    route_id = route['id']
    route_name = route['name']
    short_name = route['short_name']
    description = route['description']
    color = route['color']
    active = route['active']

    # Insert route into Routes table
    cursor.execute('''INSERT INTO Routes (id, name, short_name, description, color, active)
                      VALUES (?, ?, ?, ?, ?, ?)''', (route_id, route_name, short_name, description, color, active))

    # Insert route-stop relationships into RouteStops table
    for stop_id in route['stops']:
        cursor.execute('''INSERT INTO RouteStops (route_id, stop_id)
                          VALUES (?, ?)''', (route_id, stop_id))

# Commit changes and close connection
conn.commit()
conn.close()
