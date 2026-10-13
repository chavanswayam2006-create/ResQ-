"""
Lab 04: A* Search for Cost-Aware City Grid & 8-Puzzle Problem
Simplicity: PriorityQueue (heapq) with Manhattan & Misplaced heuristics.
"""
import heapq, json, os

COSTS = {"road": 1, "hospital": 1, "fire_station": 1, "flooded": 5, "blocked": 9999, "building": 9999}

def astar_grid(grid, start, goal):
    # Step 1: A* search on 8x8 grid considering flooded terrain cost (5) vs road (1)
    start, goal = tuple(start), tuple(goal)
    def h(pos): return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])
    
    pq = [(h(start), 0, start, [start])] # (f, g, current, path)
    best_g = {start: 0}
    nodes_explored = 0
    
    while pq:
        f, g, curr, path = heapq.heappop(pq)
        nodes_explored += 1
        if curr == goal:
            return {"path": [list(p) for p in path], "cost": g, "nodes_explored": nodes_explored}
        
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = curr[0] + dr, curr[1] + dc
            if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]):
                cell_type = grid[nr][nc]
                move_cost = COSTS.get(cell_type, 9999)
                if move_cost < 999: # passable tile
                    nxt = (nr, nc)
                    new_g = g + move_cost
                    if nxt not in best_g or new_g < best_g[nxt]:
                        best_g[nxt] = new_g
                        heapq.heappush(pq, (new_g + h(nxt), new_g, nxt, path + [nxt]))
    return {"path": [], "cost": -1, "nodes_explored": nodes_explored}

def h_misplaced(state, goal):
    # Step 2: Heuristic 1 - Count number of tiles out of place (excluding blank 0)
    return sum(1 for i in range(9) if state[i] != 0 and state[i] != goal[i])

def h_manhattan_8p(state, goal):
    # Step 3: Heuristic 2 - Sum of Manhattan distances of tiles to goal coordinates
    dist = 0
    for i, val in enumerate(state):
        if val != 0:
            target_idx = goal.index(val)
            dist += abs(i // 3 - target_idx // 3) + abs(i % 3 - target_idx % 3)
    return dist

def astar_8puzzle(start, goal=(1, 2, 3, 4, 5, 6, 7, 8, 0), heuristic="manhattan"):
    # Step 4: A* Solver for 8-Puzzle board using sliding tile operators
    h_fn = h_manhattan_8p if heuristic == "manhattan" else h_misplaced
    start, goal = tuple(start), tuple(goal)
    pq = [(h_fn(start, goal), 0, start, [start])]
    visited = {start: 0}
    nodes_explored = 0
    
    while pq:
        f, g, curr, path = heapq.heappop(pq)
        nodes_explored += 1
        if curr == goal:
            return {"solved": True, "moves": len(path) - 1, "path": [list(s) for s in path], "nodes_expanded": nodes_explored}
        
        blank = curr.index(0)
        br, bc = blank // 3, blank % 3
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = br + dr, bc + dc
            if 0 <= nr < 3 and 0 <= nc < 3:
                n_blank = nr * 3 + nc
                lst = list(curr)
                lst[blank], lst[n_blank] = lst[n_blank], lst[blank] # swap
                nxt = tuple(lst)
                new_g = g + 1
                if nxt not in visited or new_g < visited[nxt]:
                    visited[nxt] = new_g
                    heapq.heappush(pq, (new_g + h_fn(nxt, goal), new_g, nxt, path + [nxt]))
    return {"solved": False, "moves": 0, "path": [], "nodes_expanded": nodes_explored}

def run_demo():
    # Step 5: Demo run combining both grid navigation and 8-puzzle step-through
    grid_path = os.path.join(os.path.dirname(__file__), "..", "data", "city.json")
    with open(grid_path, "r", encoding="utf-8") as f:
        grid = json.load(f)["cells"]
        
    grid_res = astar_grid(grid, start=(1, 1), goal=(6, 6))
    # Simple solvable 8-puzzle instance (4 moves to goal)
    puzzle_start = (1, 2, 3, 4, 0, 6, 7, 5, 8)
    puzzle_goal = (1, 2, 3, 4, 5, 6, 7, 8, 0)
    puz_manh = astar_8puzzle(puzzle_start, puzzle_goal, "manhattan")
    puz_misp = astar_8puzzle(puzzle_start, puzzle_goal, "misplaced")
    
    return {
        "lab": "Lab 04: A* Router & 8-Puzzle Solver",
        "status": "success",
        "grid_navigation": grid_res,
        "puzzle_8": {
            "initial_state": list(puzzle_start),
            "goal_state": list(puzzle_goal),
            "manhattan_solution": puz_manh,
            "misplaced_solution": puz_misp,
            "viva_insight": "Manhattan heuristic dominates Misplaced tiles because it expands fewer or equal nodes while remaining strictly admissible."
        }
    }

if __name__ == "__main__":
    print(json.dumps(run_demo(), indent=2))
