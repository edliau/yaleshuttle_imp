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

Pathfinding via routes between bus stops is currently available via running the following command, and providing the `id`s of two bus stops:

```
python pathfinding_visualiser.py
```

Edges are directed, so adjacent bus stops may be inaccessible due to a stop being earlier along the route. 

The scraped PHP file currently used to construct the database also has stops in an incorrect order, so pathfinding information is incorrect for now.