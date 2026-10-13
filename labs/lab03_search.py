"""
Lab 03: BFS and DFS Uninformed Search on 8x8 City Grid
Simplicity: Classic Queue vs Stack implementations returning path and exploration metrics.
"""
import json, os
from collections import deque

def load_default_grid():
    # Step 1: Load city grid topography from data/city.json
    path = os.path.join(os.path.dirname(__file__), "..", "data", "city.json")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["cells"]

def get_neighbors(r, c, grid):
    # Step 2: Generate valid 4-directional moves (North, South, East, West)
    neighbors = []
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)] # N, S, W, E
    rows, cols = len(grid), len(grid[0])
    for dr, dc in directions:
        nr, nc = r + dr, c + dc
        if 0 <= nr < rows and 0 <= nc < cols:
            cell_type = grid[nr][nc]
            # Blocked cells and buildings cannot be traversed
            if cell_type not in ("blocked", "building"):
                neighbors.append((nr, nc))
    return neighbors

def bfs(grid, start, goal):
    # Step 3: Breadth-First Search using FIFO queue (guarantees fewest hops)
    start, goal = tuple(start), tuple(goal)
    queue = deque([start])
    visited = {start: None}
    visited_order = []
    
    while queue:
        curr = queue.popleft()
        visited_order.append(list(curr))
        if curr == goal:
            break
        for nxt in get_neighbors(curr[0], curr[1], grid):
            if nxt not in visited:
                visited[nxt] = curr
                queue.append(nxt)
                
    # Reconstruct shortest hop path from goal back to start
    path = []
    if goal in visited:
        curr = goal
        while curr is not None:
            path.append(list(curr))
            curr = visited[curr]
        path.reverse()
    return {"path": path, "visited_order": visited_order, "nodes_explored": len(visited_order)}

def dfs(grid, start, goal):
    # Step 4: Depth-First Search using LIFO stack (deep exploration, non-optimal)
    start, goal = tuple(start), tuple(goal)
    stack = [start]
    visited = {start: None}
    visited_order = []
    
    while stack:
        curr = stack.pop()
        visited_order.append(list(curr))
        if curr == goal:
            break
        for nxt in get_neighbors(curr[0], curr[1], grid):
            if nxt not in visited:
                visited[nxt] = curr
                stack.append(nxt)
                
    # Reconstruct path found by DFS
    path = []
    if goal in visited:
        curr = goal
        while curr is not None:
            path.append(list(curr))
            curr = visited[curr]
        path.reverse()
    return {"path": path, "visited_order": visited_order, "nodes_explored": len(visited_order)}

def run_demo(start=(1, 1), goal=(6, 6)):
    # Step 5: Execute and compare BFS vs DFS on identical start/goal coordinates
    grid = load_default_grid()
    bfs_result = bfs(grid, start, goal)
    dfs_result = dfs(grid, start, goal)
    return {
        "lab": "Lab 03: BFS & DFS Scout Search",
        "status": "success",
        "start": list(start),
        "goal": list(goal),
        "bfs": bfs_result,
        "dfs": dfs_result,
        "comparison": {
            "bfs_path_length": len(bfs_result["path"]),
            "dfs_path_length": len(dfs_result["path"]),
            "bfs_nodes_explored": bfs_result["nodes_explored"],
            "dfs_nodes_explored": dfs_result["nodes_explored"],
            "viva_insight": "BFS guarantees minimal step count (shortest path in unweighted graphs), while DFS explores deeply and produces longer trails."
        }
    }

if __name__ == "__main__":
    print(json.dumps(run_demo(), indent=2))
