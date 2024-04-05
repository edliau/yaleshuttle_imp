<?php

// Function to merge arrays while preserving keys
function merge_preserve_keys($arrays) {
    $result = array();
    foreach ($arrays as $array) {
        $result = $result + $array;
    }
    return $result;
}

// Array of relation IDs
$relations = array('10693448', 'another_relation_id');

// Array to store all nodes and edges
$all_nodes = array();
$all_edges = array();

// Initialize layer index
$layer_index = 0;

foreach ($relations as $relation) {
    // Retrieve OSM data for each relation
    $xml = simplexml_load_file("http://www.openstreetmap.org/api/0.6/relation/$relation/full");

    // Extract nodes and edges from relation XML
    $way = array();
    foreach ($xml->way as $member) {
        $way_id = (string)$member['id'];
        $nd = array();
        foreach ($member->nd as $nd_member) {
            $nd[] = (string)$nd_member['ref'];
        }
        $way[$way_id] = $nd;
    }

    $node = array();
    foreach ($xml->node as $member) {
        $node_id = (string)$member['id'];
        $node[$node_id] = array(
            'lat' => (string)$member['lat'],
            'lon' => (string)$member['lon']
        );
    }

    // Construct the graph
    $graph = array();
    foreach ($way as $way_id => $way_nodes) {
        for ($i = 0; $i < count($way_nodes) - 1; $i++) {
            $from_node = $way_nodes[$i];
            $to_node = $way_nodes[$i + 1];

            // Add edge from $from_node to $to_node
            if (!isset($graph[$from_node])) {
                $graph[$from_node] = array();
            }
            if (!isset($graph[$to_node])) {
                $graph[$to_node] = array();
            }
            $graph[$from_node][$to_node] = true;
            $graph[$to_node][$from_node] = true; // For bidirectional paths
        }
    }

    // Assign all nodes of this relation to the current layer index
    foreach ($node as $node_id => $node_data) {
        $all_nodes[$node_id] = array('layer' => $layer_index, 'data' => $node_data);
    }

    // Add edges of this relation to the all_edges array
    $all_edges = merge_preserve_keys(array($all_edges, $graph));

    // Increment layer index for the next relation
    $layer_index++;
}

// Output layered graph data into a Python script
$python_script = <<<EOD
import networkx as nx
import matplotlib.pyplot as plt

# Create a new graph
G = nx.Graph()

# Add nodes with latitude and longitude as attributes
nodes = {
EOD;

foreach ($all_nodes as $node_id => $node_info) {
    $layer = $node_info['layer'];
    $lat = $node_info['data']['lat'];
    $lon = $node_info['data']['lon'];
    $python_script .= "'$node_id': {'latitude': $lat, 'longitude': $lon, 'layer': $layer}, ";
}

$python_script = rtrim($python_script, ", ");
$python_script .= <<<EOD
}

G.add_nodes_from(nodes)

# Add edges to the graph
edges = [
EOD;

foreach ($all_edges as $node_id => $adjacent_nodes) {
    foreach ($adjacent_nodes as $adj_node => $_) {
        $python_script .= "('$node_id', '$adj_node'), ";
    }
}

$python_script = rtrim($python_script, ", ");
$python_script .= <<<EOD

]

G.add_edges_from(edges)

# Draw the layered graph
pos = nx.multipartite_layout(G, subset_key='layer')
nx.draw(G, pos, with_labels=False, node_size=10, node_color="skyblue", edge_color="gray")

plt.show()
EOD;

// Output Python script to file
file_put_contents('layered_graph_visualization.py', $python_script);

echo "Python script for layered graph generated successfully!";
?>
