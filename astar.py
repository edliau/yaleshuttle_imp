from queue import PriorityQueue

def h(p1, p2):
    # Heuristic function: Manhattan distance between two points
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)

def reconstruct_path(came_from, current):
    # Reconstruct the path by iterating through the came_from dictionary
    path = []
    while current in came_from:
        current = came_from[current]
        path.append(current)
    return path[::-1]

def a_star(graph, start, end):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {} # Dictionary to store the parent node for each node in the path
    g_score = {node: float("inf") for node in graph}
    g_score[start] = 0
    f_score = {node: float("inf") for node in graph}
    f_score[start] = h(start, end)
    open_set_hash = {start} # Set to check if a node is in the open set

    while not open_set.empty():
        current = open_set.get()[2]
        open_set_hash.remove(current)

        if current == end:
            return reconstruct_path(came_from, end)

        for neighbor in graph[current]:
            # Calculate the tentative g_score for the neighbor
            temp_g_score = g_score[current] + 1  # Assuming uniform cost for simplicity

            # Check if the tentative g_score is smaller than the current g_score for the neighbor
            if temp_g_score < g_score[neighbor]:
                # Update the came_from dictionary, indicating a better path to the neighbor
                came_from[neighbor] = current

                # Update the g_score for the neighbor with the smaller tentative g_score
                g_score[neighbor] = temp_g_score

                # If the neighbor is not in the open set, add it and mark it as open
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((g_score[neighbor] + h(neighbor, end), count, neighbor))
                    open_set_hash.add(neighbor)

    return None  # No path found
