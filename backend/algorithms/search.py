from collections import deque
import heapq


# Sample travel attraction graph
TRAVEL_GRAPH = {
    "Bangalore": {
        "Mysore": 145,
        "Coorg": 265,
        "Chikmagalur": 245
    },
    "Mysore": {
        "Bangalore": 145,
        "Ooty": 125,
        "Coorg": 120
    },
    "Coorg": {
        "Bangalore": 265,
        "Mysore": 120,
        "Chikmagalur": 160
    },
    "Chikmagalur": {
        "Bangalore": 245,
        "Coorg": 160,
        "Ooty": 220
    },
    "Ooty": {
        "Mysore": 125,
        "Chikmagalur": 220
    }
}


# 1. Breadth First Search
def bfs(graph, start, goal):
    queue = deque([[start]])
    visited = set()

    while queue:
        path = queue.popleft()
        node = path[-1]

        if node == goal:
            return path

        if node not in visited:
            visited.add(node)

            for neighbour in graph.get(node, {}):
                if neighbour not in visited:
                    queue.append(path + [neighbour])

    return None


# 2. Depth First Search
def dfs(graph, start, goal):
    stack = [[start]]
    visited = set()

    while stack:
        path = stack.pop()
        node = path[-1]

        if node == goal:
            return path

        if node not in visited:
            visited.add(node)

            for neighbour in graph.get(node, {}):
                if neighbour not in visited:
                    stack.append(path + [neighbour])

    return None


# Calculate total travel distance
def calculate_cost(graph, path):
    if not path:
        return float("inf")

    return sum(
        graph[path[i]][path[i + 1]]
        for i in range(len(path) - 1)
    )


# 3. Uniform Cost Search
def ucs(graph, start, goal):
    priority_queue = [(0, start, [start])]
    visited = set()

    while priority_queue:
        cost, node, path = heapq.heappop(priority_queue)

        if node == goal:
            return path, cost

        if node in visited:
            continue

        visited.add(node)

        for neighbour, distance in graph.get(node, {}).items():
            if neighbour not in visited:
                heapq.heappush(
                    priority_queue,
                    (cost + distance, neighbour,
                     path + [neighbour])
                )

    return None, float("inf")


# 4. A* Search
def astar(graph, start, goal, heuristic):
    priority_queue = [
        (heuristic.get(start, 0), 0, start, [start])
    ]

    visited = set()

    while priority_queue:
        f_score, cost, node, path = heapq.heappop(
            priority_queue
        )

        if node == goal:
            return path, cost

        if node in visited:
            continue

        visited.add(node)

        for neighbour, distance in graph.get(node, {}).items():
            if neighbour not in visited:
                new_cost = cost + distance
                estimated_cost = (
                    new_cost + heuristic.get(neighbour, 0)
                )

                heapq.heappush(
                    priority_queue,
                    (
                        estimated_cost,
                        new_cost,
                        neighbour,
                        path + [neighbour]
                    )
                )

    return None, float("inf")