"""
Lab 01: PEAS & Problem Formulation for Emergency Dispatch Agent
Simplicity: Plain dictionary functions describing AI Agent architecture.
"""

def get_peas():
    # Step 1: Define Performance measures (what makes the agent successful)
    performance = {
        "response_time": "Minimize elapsed minutes from report intake to arrival",
        "lives_saved": "Maximize critical patients treated and citizens rescued",
        "operational_cost": "Minimize fuel consumption and vehicle wear across terrain"
    }
    
    # Step 2: Define Environment characteristics (the 8x8 disaster city)
    environment = {
        "grid_world": "8x8 grid topology with roads, floods, and structural debris",
        "incidents": "Dynamic emergencies: fires, floods, and medical traumas",
        "road_status": "Observable transit costs: normal road (1), flood (5), blocked (inf)",
        "properties": "Partially observable, stochastic, sequential, dynamic, discrete, multi-agent"
    }
    
    # Step 3: Define Actuators (what physical or logical actions the agent executes)
    actuators = [
        "dispatch_unit(unit_id, incident_id)",
        "move_unit(unit_id, next_cell)",
        "reroute_unit(unit_id, obstacle_cell)"
    ]
    
    # Step 4: Define Sensors (how the agent perceives the world state)
    sensors = [
        "incoming_incident_reports(text, sector, hazard, people)",
        "traffic_and_flood_monitors(cell_costs)",
        "gps_unit_transponders(unit_locations, unit_status)"
    ]
    
    return {
        "Performance": performance,
        "Environment": environment,
        "Actuators": actuators,
        "Sensors": sensors
    }

def get_formulation():
    # Step 5: Formulate the classical AI search / planning problem
    return {
        "initial_state": "All response units idle at depot bases; new emergency reported in Sector S",
        "goal_state": "Appropriate rescue unit reaches incident coordinate (r, c) with minimum elapsed cost",
        "actions": ["North", "South", "East", "West"],
        "path_cost": "Sum of traversed tile transit costs: road=1, flooded=5, blocked=unreachable"
    }

def run_demo():
    # Step 6: Package demo execution payload for API and UI rendering
    peas = get_peas()
    formulation = get_formulation()
    return {
        "lab": "Lab 01: PEAS Agent & Problem Formulation",
        "status": "success",
        "peas": peas,
        "problem_formulation": formulation,
        "summary": "PEAS framework formally specifies the emergency dispatcher rational agent boundaries."
    }

if __name__ == "__main__":
    import json
    print(json.dumps(run_demo(), indent=2))
