"""
ResQ-Grid City Simulation Engine
Manages the 8x8 urban grid, emergency units, active incident queue, and time steps.
"""
import json, os, copy

CITY_JSON_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "city.json")

class CitySimulation:
    def __init__(self):
        self.load_initial_data()
        self.reset()

    def load_initial_data(self):
        with open(CITY_JSON_PATH, "r", encoding="utf-8") as f:
            self.base_data = json.load(f)

    def reset(self):
        # Reset grid, units, and empty incidents with deterministic seed state
        self.grid = copy.deepcopy(self.base_data["cells"])
        self.costs = copy.deepcopy(self.base_data["costs"])
        self.units = {u["id"]: copy.deepcopy(u) for u in self.base_data["units"]}
        self.sectors = copy.deepcopy(self.base_data["sectors"])
        self.incidents = []
        self.step_count = 0
        self.incident_seq = 100
        self.decision_log = [
            {"time": "00:00:00", "type": "system", "text": "SYSTEM INITIALIZED: 8x8 city grid active with 5 units stationed at base coordinates."}
        ]

    def log(self, text, log_type="dispatch"):
        mins = self.step_count // 60
        secs = self.step_count % 60
        timestamp = f"00:{mins:02d}:{secs:02d}"
        self.decision_log.append({"time": timestamp, "type": log_type, "text": text})

    def get_sector_center(self, sector_name):
        sec = self.sectors.get(sector_name)
        if sec:
            return sec["center"]
        # Default fallback
        return [3, 3]

    def add_incident(self, incident_data):
        self.incident_seq += 1
        incident_id = f"INC-{self.incident_seq}"
        incident_data["id"] = incident_id
        incident_data["status"] = "open"
        self.incidents.append(incident_data)
        return incident_data

    def step(self):
        self.step_count += 1
        actions_taken = 0
        
        for u_id, unit in self.units.items():
            if unit["status"] == "responding" and unit["route"]:
                # Advance 1 step along assigned A* route
                next_pos = unit["route"].pop(0)
                unit["pos"] = next_pos
                actions_taken += 1
                
                # Check if unit arrived at target
                if not unit["route"]:
                    inc_id = unit["assigned_incident"]
                    unit["status"] = "idle"
                    unit["assigned_incident"] = None
                    # Mark incident resolved
                    for inc in self.incidents:
                        if inc["id"] == inc_id and inc["status"] != "resolved":
                            inc["status"] = "resolved"
                            self.log(f"INCIDENT RESOLVED: Unit {unit['id']} ({unit['name']}) successfully mitigated {inc_id} at Sector {inc['sector']}.", "resolved")
                            break
                            
        if actions_taken == 0:
            self.log(f"SIM STEP {self.step_count}: All sectors monitored; no pending unit movements in progress.", "patrol")
            
        return self.get_state()

    def get_state(self):
        # Sort queue: open first (sorted by urgency descending), then resolved
        open_incs = sorted([i for i in self.incidents if i["status"] != "resolved"], 
                           key=lambda x: x.get("urgency", 0), reverse=True)
        resolved_incs = [i for i in self.incidents if i["status"] == "resolved"]
        
        return {
            "step": self.step_count,
            "grid": self.grid,
            "units": list(self.units.values()),
            "incidents": open_incs + resolved_incs,
            "sectors": self.sectors,
            "log": list(reversed(self.decision_log[-20:])) # last 20 entries, newest first
        }

# Global singleton simulator instance
city_sim = CitySimulation()
