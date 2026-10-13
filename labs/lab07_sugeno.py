"""
Lab 07: Mamdani vs Sugeno Defuzzification Comparison
Simplicity: Pure numpy 0th-order Sugeno weighted-average vs Mamdani centroid.
"""
from labs.lab06_fuzzy import fuzzy_urgency

def tri(x, a, b, c):
    # Step 1: Standard triangular membership helper
    if x <= a or x >= c:
        return 0.0
    return (x - a) / (b - a) if x <= b else (c - x) / (c - b)

def sugeno_urgency(h, p):
    # Step 2: Compute input fuzzy membership degrees
    h_low = 1.0 if h <= 0 else (tri(h, -1, 0, 50) if h < 50 else 0.0)
    h_med = tri(h, 20, 50, 80)
    h_high = 1.0 if h >= 100 else (tri(h, 50, 100, 101) if h > 50 else 0.0)

    p_few = 1.0 if p <= 0 else (tri(p, -1, 0, 50) if p < 50 else 0.0)
    p_some = tri(p, 20, 50, 80)
    p_many = 1.0 if p >= 100 else (tri(p, 50, 100, 101) if p > 50 else 0.0)

    # Step 3: Firing strength (w_i = min(mu_h, mu_p)) and singleton constants (z_i)
    # Low = 20, Med = 50, High = 80
    rules = [
        (min(h_low, p_few), 20.0),
        (min(h_low, p_some), 20.0),
        (min(h_low, p_many), 50.0),
        (min(h_med, p_few), 20.0),
        (min(h_med, p_some), 50.0),
        (min(h_med, p_many), 80.0),
        (min(h_high, p_few), 50.0),
        (min(h_high, p_some), 80.0),
        (min(h_high, p_many), 80.0)
    ]
    # Step 4: Weighted average defuzzification: sum(w*z) / sum(w)
    total_w = sum(w for w, _ in rules)
    if total_w == 0:
        return 50.0
    sugeno_val = sum(w * z for w, z in rules) / total_w
    return round(float(sugeno_val), 2)

def compare(h, p):
    # Step 5: Direct pairwise comparison of Mamdani vs Sugeno output
    mamdani = fuzzy_urgency(h, p)
    sugeno = sugeno_urgency(h, p)
    return {
        "hazard": h,
        "people": p,
        "mamdani": mamdani,
        "sugeno": sugeno,
        "abs_diff": round(abs(mamdani - sugeno), 2)
    }

def run_demo():
    # Step 6: Evaluate 5 representative test cases across the emergency domain
    test_cases = [
        (10, 10),  # Minor event (Low / Few)
        (35, 45),  # Emerging incident (Med / Some)
        (80, 20),  # High hazard, sparse population
        (40, 90),  # Moderate hazard, dense crowd
        (95, 95)   # Catastrophic multi-casualty fire
    ]
    results = [compare(h, p) for h, p in test_cases]
    return {
        "lab": "Lab 07: Mamdani vs Sugeno Defuzzification",
        "status": "success",
        "comparison_table": results,
        "viva_insight": "Sugeno defuzzification uses algebraic weighted averaging of crisp constants, making it computationally faster than Mamdani numerical integration (centroid)."
    }

if __name__ == "__main__":
    import json
    print(json.dumps(run_demo(), indent=2))
