import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import networkx as nx

# Parse XML data
tree = ET.parse('data.xml')
root = tree.getroot()

# Create a directed graph
G = nx.DiGraph()

# Extract nodes and their coordinates
nodes = {}
for node in root.findall('.//node'):
    node_id = node.attrib['id']
    lat = float(node.attrib['lat'])
    lon = float(node.attrib['lon'])
    nodes[node_id] = (lon, lat)  # Assuming lon, lat order

# Extract ways and their constituent nodes
for way in root.findall('.//way'):
    way_id = way.attrib['ref']
    way_nodes = [nd.attrib['ref'] for nd in way.findall('.//nd')]
    G.add_edges_from(zip(way_nodes[:-1], way_nodes[1:]), id=way_id)

# Set coordinates as node attributes
nx.set_node_attributes(G, nodes, 'pos')

# Draw the graph
pos = nx.get_node_attributes(G, 'pos')
nx.draw(G, pos, with_labels=True, node_size=10)
plt.show()
