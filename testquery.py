import requests
import json
import time

url = "https://yale.downtownerapp.com/routes_buses.php"

while True:
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = json.loads(response.text)
            print(json.dumps(data, indent=4))
        else:
            print(f"Error: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

    time.sleep(5)