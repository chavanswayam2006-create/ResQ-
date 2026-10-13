"""
Lab 02: Prolog Knowledge Base & First-Order Horn Clause Inference Mirror
Simplicity: Pure Python dictionary pattern-matching mirroring Prolog logic.
"""
import os

# Step 1: Python mirror of facts defined in data/knowledge_base.pl
UNITS = {
    "A1": "ambulance",
    "A2": "ambulance",
    "F1": "fire_truck",
    "F2": "fire_truck",
    "B1": "rescue_boat"
}

NEEDS = {
    "fire": "fire_truck",
    "flood": "rescue_boat",
    "medical": "ambulance"
}

def ask(query):
    # Step 2: Unify query string against facts and deduction rules
    # Supported queries: 'suitable(U, fire)', 'suitable(U, flood)', 'needs(K, T)', etc.
    results = []
    q = query.strip().lower()
    
    if q.startswith("suitable"):
        # Extract incident kind from 'suitable(U, <kind>)'
        kind = q.split(",")[-1].replace(")", "").strip()
        required_type = NEEDS.get(kind)
        if required_type:
            # Rule: suitable(U, I) :- unit(U, T), needs(Kind, T)
            for uid, utype in UNITS.items():
                if utype == required_type:
                    results.append({"unit": uid, "type": utype, "matches_incident": kind})
    elif q.startswith("needs"):
        # Match needs(Kind, Type)
        for k, t in NEEDS.items():
            results.append({"incident_kind": k, "required_unit": t})
    elif q.startswith("unit"):
        # Match unit(Id, Type)
        for uid, utype in UNITS.items():
            results.append({"unit": uid, "type": utype})
            
    return results

def find_suitable_units(incident_type):
    # Step 3: Fast function used by the simulator pipeline to get eligible units
    req = NEEDS.get(incident_type.lower())
    if not req:
        return []
    return [uid for uid, utype in UNITS.items() if utype == req]

def get_prolog_source():
    # Step 4: Load Prolog file text to show on UI side-by-side
    kb_path = os.path.join(os.path.dirname(__file__), "..", "data", "knowledge_base.pl")
    if os.path.exists(kb_path):
        with open(kb_path, "r", encoding="utf-8") as f:
            return f.read()
    return "% Knowledge base file not found."

def run_demo(query="suitable(U, fire)"):
    # Step 5: Evaluate query and package with .pl source code
    bindings = ask(query)
    prolog_code = get_prolog_source()
    return {
        "lab": "Lab 02: Prolog Rule Brain",
        "status": "success",
        "query": query,
        "results": bindings,
        "prolog_code": prolog_code,
        "summary": f"Query '{query}' resolved {len(bindings)} unified solutions via Horn clause deduction."
    }

if __name__ == "__main__":
    import json
    print(json.dumps(run_demo(), indent=2))
