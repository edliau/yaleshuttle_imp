# yaleshuttle-imp
an improved version of the Yale Shuttle Application for CPSC419

Install the project's dependencies using:
```
pip install -r requirements.txt
```

To run project:

Run the following command:

```
python app.py
```

In a seperate terminal:
```
python data.py
```

The app will be available at 127.0.0.1:3000/home.

Pathfinding:

Pathfinding via routes between bus stops can be visualised via navigating to the `extras` folder, passing the following command to the terminal, and providing the `id`s of two bus stops:

```
python pathfinding_visualiser.py
```

Edges are directed, so adjacent bus stops may be inaccessible due to a stop being earlier along the route, or the routing may suggest one large loop. Pathfinding is done by constructing a directed graph using coordinates and bus route relations scraped from the Downtowner App's php file, with edge weights being the haversine distance between bus stops. This is admittedly not perfect as it does not account for actual road conditions, but we'll go with it for now. The pathfilding function is available at `route_finder.py`

Continuations: Adjust for bus arrival timings to suggest routes? Have preset time values allocated to different haversine values? route_database_builder is the runner code which will update the database, currently it ignores which routes are active/inactive, maybe we can set the runner file to poll for activity/ inactivity at specficic times (when bus times change?).