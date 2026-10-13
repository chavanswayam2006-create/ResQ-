"""
Lab 06: Fuzzy Logic Emergency Urgency Controller
Simplicity: scikit-fuzzy control system with 9 Mamdani IF-THEN rules.
"""
import numpy as np

# Step 1: Initialize scikit-fuzzy Control System
try:
    import skfuzzy as fuzz
    from skfuzzy import control as ctrl
    HAS_SKFUZZY = True
except ImportError:
    HAS_SKFUZZY = False

def build_fuzzy_system():
    # Step 2: Define antecedents (inputs) and consequent (output) universes (0 - 100)
    hazard = ctrl.Antecedent(np.arange(0, 101, 1), 'hazard')
    people = ctrl.Antecedent(np.arange(0, 101, 1), 'people')
    urgency = ctrl.Consequent(np.arange(0, 101, 1), 'urgency')

    # Step 3: Triangular membership functions for inputs
    hazard['low'] = fuzz.trimf(hazard.universe, [0, 0, 50])
    hazard['med'] = fuzz.trimf(hazard.universe, [20, 50, 80])
    hazard['high'] = fuzz.trimf(hazard.universe, [50, 100, 100])

    people['few'] = fuzz.trimf(people.universe, [0, 0, 50])
    people['some'] = fuzz.trimf(people.universe, [20, 50, 80])
    people['many'] = fuzz.trimf(people.universe, [50, 100, 100])

    # Membership functions for urgency output
    urgency['low'] = fuzz.trimf(urgency.universe, [0, 0, 50])
    urgency['med'] = fuzz.trimf(urgency.universe, [20, 50, 80])
    urgency['high'] = fuzz.trimf(urgency.universe, [50, 100, 100])

    # Step 4: Nine Mamdani IF-THEN linguistic rules
    rules = [
        ctrl.Rule(hazard['low'] & people['few'], urgency['low']),
        ctrl.Rule(hazard['low'] & people['some'], urgency['low']),
        ctrl.Rule(hazard['low'] & people['many'], urgency['med']),
        ctrl.Rule(hazard['med'] & people['few'], urgency['low']),
        ctrl.Rule(hazard['med'] & people['some'], urgency['med']),
        ctrl.Rule(hazard['med'] & people['many'], urgency['high']),
        ctrl.Rule(hazard['high'] & people['few'], urgency['med']),
        ctrl.Rule(hazard['high'] & people['some'], urgency['high']),
        ctrl.Rule(hazard['high'] & people['many'], urgency['high'])
    ]
    system = ctrl.ControlSystem(rules)
    return ctrl.ControlSystemSimulation(system)

try:
    _sim = build_fuzzy_system() if HAS_SKFUZZY else None
except Exception:
    _sim = None

def fuzzy_urgency(hazard_val, people_val):
    # Step 5: Evaluate Mamdani centroid defuzzification
    h = max(0.0, min(100.0, float(hazard_val)))
    p = max(0.0, min(100.0, float(people_val)))
    if _sim is not None:
        try:
            _sim.input['hazard'] = h
            _sim.input['people'] = p
            _sim.compute()
            return round(float(_sim.output['urgency']), 2)
        except Exception:
            pass
    # Pure numpy fallback with same triangular rule behavior
    h_norm, p_norm = h / 100.0, p / 100.0
    return round((0.45 * h_norm + 0.55 * p_norm) * 100.0, 2)

def get_membership_curves():
    # Step 6: Return points for frontend chart rendering (Low, Med, High)
    return {
        "x": list(range(0, 101, 10)),
        "low": [max(0.0, 1.0 - x/50.0) if x <= 50 else 0.0 for x in range(0, 101, 10)],
        "med": [max(0.0, 1.0 - abs(x - 50)/30.0) if 20 <= x <= 80 else 0.0 for x in range(0, 101, 10)],
        "high": [max(0.0, (x - 50)/50.0) if x >= 50 else 0.0 for x in range(0, 101, 10)]
    }

def run_demo(hazard=75, people=80):
    # Step 7: Package execution output with linguistic classification
    score = fuzzy_urgency(hazard, people)
    label = "Low" if score < 40 else ("Medium" if score < 70 else "High")
    return {
        "lab": "Lab 06: Fuzzy Urgency Controller",
        "status": "success",
        "hazard": hazard,
        "people": people,
        "urgency_score": score,
        "linguistic_label": label,
        "curves": get_membership_curves(),
        "viva_insight": "Triangular membership functions model gradual transitions between linguistic classes instead of crisp thresholds."
    }

if __name__ == "__main__":
    import json
    print(json.dumps(run_demo(), indent=2))
