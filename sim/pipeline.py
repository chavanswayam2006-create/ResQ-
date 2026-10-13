"""
ResQ-Grid AI Reasoning & Dispatch Pipeline
Chains Labs 01-10 into an autonomous emergency decision system.
"""
from sim.city import city_sim
from labs.lab02_prolog import find_suitable_units
from labs.lab03_search import bfs
from labs.lab04_astar import astar_grid
from labs.lab05_minimax import advise_sector
from labs.lab06_fuzzy import fuzzy_urgency
from labs.lab07_sugeno import sugeno_urgency
from labs.lab08_neuro_fuzzy import predict_response
from labs.lab09_neural_learning import classify_critical

def detect_incident_type(text, hazard=50, people=50):
    # Step 1: Rule-based keyword classification from radio transcript
    t = text.lower()
    if any(k in t for k in ["fire", "flame", "smoke", "blaze", "burn"]):
        return "fire"
    if any(k in t for k in ["flood", "water", "submerge", "overflow", "drown", "boat"]):
        return "flood"
    if any(k in t for k in ["medic", "injur", "patient", "trauma", "crash", "collision", "cardiac", "casualt"]):
        return "medical"
    # Sensible fallback
    return "fire" if hazard >= people else "medical"

def handle_incident(text, sector, hazard, people):
    # Step 2: Detect incident type
    inc_type = detect_incident_type(text, hazard, people)
    target_pos = city_sim.get_sector_center(sector)

    # Step 3: Compute urgency across Fuzzy (Lab 6), Sugeno (Lab 7), and Neuro-Fuzzy (Lab 8)
    urg_mamdani = fuzzy_urgency(hazard, people)
    urg_sugeno = sugeno_urgency(hazard, people)
    nf_pred = predict_response(hazard, people)
    final_urgency = nf_pred["urgency"]
    urgency_level = nf_pred["level"]

    # Step 4: Classify Critical vs Routine using Perceptron (Lab 9)
    crit_pred = classify_critical(people / 100.0, hazard / 100.0, 0.4)
    is_critical = crit_pred["critical"]

    # Step 5: Logic rule deduction for eligible units (Lab 2)
    eligible_ids = find_suitable_units(inc_type)
    
    # Step 6: Find best candidate unit using cost-aware A* search (Lab 4)
    best_unit = None
    best_astar = None
    min_cost = float("inf")

    # First check idle eligible units
    candidate_units = [city_sim.units[uid] for uid in eligible_ids if city_sim.units[uid]["status"] == "idle"]
    # Fallback to any idle unit if eligible ones are busy
    if not candidate_units:
        candidate_units = [u for u in city_sim.units.values() if u["status"] == "idle"]
    # Fallback to any eligible unit even if currently in transit
    if not candidate_units:
        candidate_units = [city_sim.units[uid] for uid in eligible_ids]

    for unit in candidate_units:
        route_res = astar_grid(city_sim.grid, unit["pos"], target_pos)
        if route_res["cost"] >= 0 and route_res["cost"] < min_cost:
            min_cost = route_res["cost"]
            best_unit = unit
            best_astar = route_res

    # Fallback in rare case no route found
    if best_unit is None:
        best_unit = list(city_sim.units.values())[0]
        best_astar = astar_grid(city_sim.grid, best_unit["pos"], target_pos)

    # Step 7: Compare against unweighted BFS search (Lab 3)
    bfs_res = bfs(city_sim.grid, best_unit["pos"], target_pos)

    # Step 8: Multi-incident adversarial strategy advisory via Minimax (Lab 5)
    open_sectors = [i["sector"] for i in city_sim.incidents if i["status"] != "resolved"]
    if sector not in open_sectors:
        open_sectors.append(sector)
    
    minimax_advice = sector
    if len(open_sectors) >= 2:
        minimax_advice = advise_sector(open_sectors, damaged_sectors=[sector])

    # Step 9: Register incident and assign unit route in simulator
    incident_record = {
        "text": text,
        "type": inc_type,
        "sector": sector,
        "target_pos": target_pos,
        "hazard": hazard,
        "people": people,
        "urgency": final_urgency,
        "urgency_level": urgency_level,
        "is_critical": is_critical,
        "assigned_unit": best_unit["id"],
        "assigned_unit_name": best_unit["name"],
        "astar_cost": best_astar["cost"],
        "astar_hops": len(best_astar["path"]) - 1 if best_astar["path"] else 0,
        "bfs_hops": len(bfs_res["path"]) - 1 if bfs_res["path"] else 0,
        "minimax_priority_sector": minimax_advice,
        "comparison": {
            "mamdani": urg_mamdani,
            "sugeno": urg_sugeno,
            "neuro_fuzzy": final_urgency
        }
    }
    
    # Save into city simulator
    added_inc = city_sim.add_incident(incident_record)
    
    # Assign path to unit (pop first tile since unit is already on it)
    full_route = list(best_astar["path"])
    unit_route = full_route[1:] if len(full_route) > 1 else full_route
    best_unit["status"] = "responding"
    best_unit["assigned_incident"] = added_inc["id"]
    best_unit["route"] = unit_route

    # Append clear, viva-friendly natural language log entry
    crit_tag = "CRITICAL" if is_critical else "ROUTINE"
    log_text = (f"DISPATCH [{added_inc['id']}]: {inc_type.upper()} in {sector}. "
                f"Urgency={final_urgency}% ({urgency_level}, Neuro-Fuzzy), {crit_tag} (Perceptron). "
                f"Assigned {best_unit['id']} ({best_unit['name']}) via A* cost={best_astar['cost']} "
                f"(BFS={incident_record['bfs_hops']} hops). Strategy priority: {minimax_advice}.")
    city_sim.log(log_text, "dispatch")

    return {
        "status": "success",
        "incident": added_inc,
        "city_state": city_sim.get_state()
    }
