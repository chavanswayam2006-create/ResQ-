"""
Lab 05: Minimax Adversarial Strategy Advisor (Disaster vs Responder)
Simplicity: 3x3 Sectors game tree where MAX protects and MIN disaster spreads.
"""
# Step 1: Population at risk across 9 city sectors (A to I)
SECTOR_POPULATION = {
    "Sector A": 50, "Sector B": 80, "Sector C": 40,
    "Sector D": 95, "Sector E": 120, "Sector F": 60,
    "Sector G": 70, "Sector H": 85, "Sector I": 110
}

# Sector adjacency map for realistic disaster spreading across 3x3 grid
ADJACENCY = {
    "Sector A": ["Sector B", "Sector D"],
    "Sector B": ["Sector A", "Sector C", "Sector E"],
    "Sector C": ["Sector B", "Sector F"],
    "Sector D": ["Sector A", "Sector E", "Sector G"],
    "Sector E": ["Sector B", "Sector D", "Sector F", "Sector H"],
    "Sector F": ["Sector C", "Sector E", "Sector I"],
    "Sector G": ["Sector D", "Sector H"],
    "Sector H": ["Sector G", "Sector E", "Sector I"],
    "Sector I": ["Sector F", "Sector H"]
}

def evaluate_utility(state):
    # Step 2: Utility = Total people saved in protected sectors minus people in damaged sectors
    protected_people = sum(SECTOR_POPULATION.get(s, 0) for s in state["protected"])
    damaged_people = sum(SECTOR_POPULATION.get(s, 0) for s in state["damaged"])
    return protected_people - damaged_people

def minimax(state, depth, is_max, alpha=float("-inf"), beta=float("inf")):
    # Step 3: Recursive Minimax with Alpha-Beta pruning up to depth <= 4
    # Terminal condition: depth limit reached or no candidate sectors remain
    candidates = [s for s in SECTOR_POPULATION if s not in state["protected"] and s not in state["damaged"]]
    if depth == 0 or not candidates:
        return evaluate_utility(state), None

    if is_max: # MAX Responder turn: choose sector that maximizes saved lives
        max_eval = float("-inf")
        best_move = candidates[0]
        for sector in candidates:
            new_state = {
                "protected": state["protected"] | {sector},
                "damaged": set(state["damaged"])
            }
            val, _ = minimax(new_state, depth - 1, False, alpha, beta)
            if val > max_eval:
                max_eval = val
                best_move = sector
            alpha = max(alpha, eval if (eval := val) else val)
            if beta <= alpha:
                break
        return max_eval, best_move
    else: # MIN Disaster turn: choose sector that maximizes damage (minimizes utility)
        min_eval = float("inf")
        best_move = candidates[0]
        for sector in candidates:
            new_state = {
                "protected": set(state["protected"]),
                "damaged": state["damaged"] | {sector}
            }
            val, _ = minimax(new_state, depth - 1, True, alpha, beta)
            if val < min_eval:
                min_eval = val
                best_move = sector
            beta = min(beta, val)
            if beta <= alpha:
                break
        return min_eval, best_move

def advise_sector(open_sectors, damaged_sectors=None):
    # Step 4: Advisor function used by simulator when 2+ incidents compete for dispatch
    damaged = set(damaged_sectors) if damaged_sectors else set()
    initial_state = {"protected": set(), "damaged": damaged}
    # Filter search to focus on open incident sectors if provided
    val, chosen = minimax(initial_state, depth=4, is_max=True)
    if chosen not in open_sectors and open_sectors:
        # Pick highest population among open sectors if minimax selected outside
        chosen = max(open_sectors, key=lambda s: SECTOR_POPULATION.get(s, 0))
    return chosen

def run_demo():
    # Step 5: Demo scenario with initial disaster in Sector E (Central Crossing)
    demo_state = {"protected": set(), "damaged": {"Sector E"}}
    score, best_action = minimax(demo_state, depth=4, is_max=True)
    return {
        "lab": "Lab 05: Minimax Adversarial Strategy Advisor",
        "status": "success",
        "scenario": "Disaster active at Sector E (120 people). MAX responder computing depth-4 optimal defense.",
        "best_move": best_action,
        "projected_utility_score": score,
        "sector_populations": SECTOR_POPULATION,
        "viva_insight": "Minimax models disaster spread as an adversarial agent to protect high-density sectors before containment fails."
    }

if __name__ == "__main__":
    import json
    print(json.dumps(run_demo(), indent=2))
