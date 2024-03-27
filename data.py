import sqlite3
import requests
import json
import time

url = "https://yale.downtownerapp.com/routes_buses.php"

connection = sqlite3.connect("data.db")
print(connection.total_changes)
cursor = connection.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS shuttles (id TEXT, name TEXT, lat TEXT, lon TEXT, heading TEXT, route TEXT, lastStop TEXT, lastUpdate TEXT)")

while True:
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = json.loads(response.text)
            for element in data:
                cursor.execute("INSERT INTO shuttles (id,name,lat,lon,heading,route,lastStop,lastUpdate) VALUES (?,?,?,?,?,?,?,?)", (element["id"], element["name"], element["lat"], element["lon"], element["heading"],element["route"],element["lastStop"],element["lastUpdate"]))

            connection.commit()

            print(data)
            # cursor.execute("SELECT * FROM shuttles")
            # rows = cursor.fetchall()

            # for row in rows:
            #     print(row)

            # print(connection.total_changes)
            time.sleep(5)
        else:
            print(f"Error: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")