from flask import Flask, jsonify, request, make_response, redirect, url_for, render_template
import sqlite3
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/home', methods=['GET'])
def index():
    html = render_template('index.html')
    response = make_response(html)
    return response


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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)