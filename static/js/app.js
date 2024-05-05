mapboxgl.accessToken = 'pk.eyJ1Ijoic29seWNhIiwiYSI6ImNpejhqZmlmNjAwMDUycW82N3g2dG05ZHYifQ.CKn9Ww3bjhirdny-PIZqdg';
const map = new mapboxgl.Map({
    container: 'map-container',
    style: 'mapbox://styles/mapbox/streets-v11',
    center: [-72.923995, 41.309798],
    zoom: 12
});

const instructionsOverlay = document.createElement('div');
instructionsOverlay.className = 'instructions-overlay';
document.body.appendChild(instructionsOverlay);

let markers = {};
let stops_arr = {};
let coordtoggle = true;
var startCoordList = null;
var endCoordList = null;

const colorDict = {
    '1': '#4472C4',
    '2': '#ED7D31',
    '3': '#FF0000',
    '8': '#DB1AD2',
    '9': '#70AD46',
    '10': '#6F30A1',
    '11': '#7E6001',
    '12': '#F6BE00'
};

const routesNames = {
    '1': 'Blue',
    '2': 'Orange',
    '3': 'Red',
    '8': 'Pink',
    '9': 'Green',
    '10': 'Purple',
    '11': 'Brown',
    '12': 'Yellow'
};

function getMarkerColor(route) {
    return colorDict[route] || '#000000'; // Assign default color if not found in the dictionary
}

function updateMarkers(data) {
    data.forEach(row => {
        const { id, name, lat, lon, heading, route, lastStop, lastUpdate } = row;
        const key = `${route}-${id}`;
        if (markers[key]) {
            // Update the position of the existing marker
            markers[key].setLngLat([lon, lat]);
        } else {
            // Create a new marker
            const color = getMarkerColor(route);
            markers[key] = new mapboxgl.Marker({
                color: color
            })
                .setLngLat([lon, lat])
                .addTo(map);
        }

        markers[key].setPopup(
            new mapboxgl.Popup()
                .setHTML(`
                <h3>${routesNames[route]} Shuttle</h3>
                <p>Name: ${name}</p>
                <p>Heading: ${heading}°</p>
                <p>Last stop: ${lastStop}</p>
                <p>Last update: ${new Date(lastUpdate * 1000).toLocaleString()}</p>
              `)
        );
    });
}



function updateStops(stops) {
    console.log("updateStops called");
    console.log("Stops:", stops);
    console.log("Stops array:", stops_arr);


    stops.forEach((row, index) => {
        const { id, name, lat, lon } = row;
        const key = `${id}`;
        const dotElement = document.createElement('div');
        dotElement.className = 'dot-marker';
        // console.log(`Processing stop ${index + 1} with id: ${id}`);

        // console.log("Stops array:", stops_arr);
        if (stops_arr[key]) {
            // console.log(`Marker already exists for stop with id: ${id}`);
            // Update the position of the existing marker
            stops_arr[key].setLngLat([lon, lat]);
        } else {
            // console.log(`Creating new marker for stop with id: ${id}`);
            // Create a new marker
            // console.log(lon + " " + lat)
            stops_arr[key] = new mapboxgl.Marker({
                element: dotElement,
            })
                .setLngLat([lon, lat])
                .addTo(map);

            stops_arr[key].setPopup(
                new mapboxgl.Popup()
                    .setHTML(`
              <p>Name: ${name}</p>
            `)
            );
        }
    })
}

function fetchAndUpdateData() {
    fetch('http://localhost:3000/data')
        .then(response => response.json())
        .then(data => {
            updateMarkers(data);
        })
        .catch(error => {
            console.error('Error fetching data:', error);
        });
}

function fetchAndUpdateStops() {
    // console.log("fetchAndUpdateStops called");
    fetch('http://localhost:3000/stops')
        .then(response => response.json())
        .then(data => {
            // console.log(data);
            updateStops(data);
        })
        .catch(error => {
            console.error('Error fetching data:', error);
        });
}

let currController = null;
async function findShortestRoute(startCoord, endCoord) {

    if (currController) {
        currController.abort();
    }

    const abortcont = new AbortController();
    currController = abortcont;

    fetch('/find-shortest-route', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        signal: abortcont.signal,
        body: JSON.stringify({ start: startCoord, end: endCoord })
    })
        .then(response => {
            if (response.ok) {
                return response.json(); // Return the GeoJSON response
            } else {
                throw new Error('Failed to find shortest route.');
            }
        })
        .then(routeData => {
            // console.log('Route data:', routeData);
            const coordinates = routeData.route_coords;
            const naturalLanguageInstructions = routeData.natural_language_instructions;
            // console.log('Route coordinates:', coordinates);
            const accessToken = 'YOUR_MAPBOX_ACCESS_TOKEN';
            const coords = coordinates.map(coord => coord.join(',')).join(';');
            const encodedString = encodeURIComponent(coords).replace(/,/g, '%2C');
            const url = `https://api.mapbox.com/directions/v5/mapbox/driving/${encodedString}?access_token=${mapboxgl.accessToken}&geometries=geojson`;
            // console.log('URL:', url);

            // Update the instructions overlay with the new instructions
            instructionsOverlay.innerHTML = `
          <div class="instructions-content">
          <h3>Route Instructions</h3>
            <ul>
              ${naturalLanguageInstructions.map(instruction => `<li class="inst">${instruction}</li>`).join('')}
            </ul>
          <button class="close-button">Close</button>
        </div>
        `;

            // Show the instructions overlay
            instructionsOverlay.style.display = 'block';

            // Add event listener to close the instructions overlay when the close button is clicked
            const closeButton = instructionsOverlay.querySelector('.close-button');
            closeButton.addEventListener('click', () => {
                instructionsOverlay.style.display = 'none';
            });

            return fetch(url);
        })
        .then(response => {
            // console.log('Response:', response);
            return response.json();
        })
        .then(data => {
            const route = data.routes[0].geometry;

            // Remove the existing 'route' source and layer if they exist
            if (map.getSource('route')) {
                map.removeLayer('route');
                map.removeSource('route');
            }

            // Add a new source with a unique ID
            map.addSource('route', {
                type: 'geojson',
                data: {
                    type: 'Feature',
                    geometry: route
                }
            });

            // Add the route line to the map
            map.addLayer({
                id: 'route',
                type: 'line',
                source: 'route',
                paint: {
                    'line-color': '#3887be',
                    'line-width': 5,
                    'line-opacity': 0.75
                }
            });
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

//onClick, update the end coordinates, and pass them to the server to find the shortest route. Also checks for user location.
map.on('click', (e) => {
    if (startCoordList == null) {
        document.getElementById('coord1').innerHTML = "User location not found! Please ensure your location services are enabled.";
    } else {
        endCoordList = [e.lngLat.lat, e.lngLat.lng];
        document.getElementById('coord2').innerHTML = "End Coord: " + endCoordList.toString();

        findShortestRoute(startCoordList, endCoordList);
    }
});

/*
  For geolocation to work, the browser needs to allow the local server access to the location. Because the connection isn't secure,
  it is blocked by default for security reasons. You can disable it like so:
  https://stackoverflow.com/questions/57450093/browser-says-camera-blocked-to-protect-your-privacy
  (This says for the camera, but it applies to all browser permissions.)
  After that you can click the button on the top right to give the map your location.
*/
// START Geolocation
const geolocate = new mapboxgl.GeolocateControl({
    positionOptions: {
        enableHighAccuracy: true
    },
    trackUserLocation: true
});

// Move the geolocate control to the bottom left
map.addControl(geolocate, 'bottom-left');

geolocate.on('geolocate', (e) => {
    var lon = e.coords.longitude;
    var lat = e.coords.latitude;
    startCoordList = [lat, lon];
    document.getElementById('coord1').innerHTML = "Start Coord: " + startCoordList.toString();
    document.getElementById('coord2').innerHTML = "End Coord: ";
    console.log('A geolocate event has occurred.');
});
// END Geolocation

fetchAndUpdateData();

console.log("Fetching stops");
fetchAndUpdateStops();
setInterval(fetchAndUpdateData, 10000); // Update every 10 seconds