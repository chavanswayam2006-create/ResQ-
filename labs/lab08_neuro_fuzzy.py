"""
Lab 08: Neuro-Fuzzy Hybrid Urgency Predictor
Simplicity: MLPRegressor trained on Mamdani dataset with fuzzy level labeling.
Zero external dataframe dependencies (pure csv + numpy).
"""
import os, csv, warnings, numpy as np
from labs.lab06_fuzzy import fuzzy_urgency
warnings.filterwarnings("ignore")

try:
    from sklearn.neural_network import MLPRegressor
    from sklearn.preprocessing import MinMaxScaler
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

CSV_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "incidents_history.csv"))

def ensure_dataset():
    # Step 1: Read or generate ~300 synthetic incident records using pure csv & numpy
    hazards, peoples, urgencies = [], [], []
    if os.path.exists(CSV_PATH):
        try:
            with open(CSV_PATH, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    hazards.append(float(row["hazard_intensity"]))
                    peoples.append(float(row["people_at_risk"]))
                    urgencies.append(float(row["urgency"]))
            if len(hazards) >= 50:
                return np.column_stack([hazards, peoples]), np.array(urgencies)
        except Exception:
            pass # fallback to in-memory generation

    # Generate synthetic training set deterministically (seed 42)
    rng = np.random.RandomState(42)
    hazards = rng.uniform(0, 100, 300)
    peoples = rng.uniform(0, 100, 300)
    noise = rng.normal(0, 2.0, 300)
    urgencies = [float(np.clip(fuzzy_urgency(h, p) + n, 0.0, 100.0))
                 for h, p, n in zip(hazards, peoples, noise)]

    # Attempt to write if filesystem allows (safe on read-only serverless)
    try:
        os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)
        with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["hazard_intensity", "people_at_risk", "urgency"])
            for h, p, u in zip(hazards, peoples, urgencies):
                writer.writerow([round(h, 2), round(p, 2), round(u, 2)])
    except Exception:
        pass

    return np.column_stack([hazards, peoples]), np.array(urgencies)

# Step 2: Initialize scaler and train lightweight MLP neural network
_X, _y = ensure_dataset()
if HAS_SKLEARN:
    _scaler = MinMaxScaler()
    _X_scaled = _scaler.fit_transform(_X)
    _mlp = MLPRegressor(hidden_layer_sizes=(8, 8), max_iter=250, random_state=42)
    _mlp.fit(_X_scaled, _y)
else:
    _scaler, _mlp = None, None

def predict_response(hazard, people):
    # Step 3: Predict urgency and apply fuzzy linguistic labeling (clamped 0-100)
    h_val = float(np.clip(hazard, 0, 100))
    p_val = float(np.clip(people, 0, 100))
    if HAS_SKLEARN and _mlp is not None and _scaler is not None:
        x_scaled = _scaler.transform([[h_val, p_val]])
        raw_pred = float(_mlp.predict(x_scaled)[0])
        pred = float(np.clip(raw_pred, 0.0, 100.0))
    else:
        # Graceful mathematical approximation if sklearn is missing
        pred = float(np.clip(0.48 * h_val + 0.52 * p_val, 0.0, 100.0))

    pred = round(pred, 2)
    level = "Low" if pred < 40.0 else ("Medium" if pred < 70.0 else "High")
    return {"urgency": pred, "level": level, "hazard": h_val, "people": p_val}

def evaluate_test_cases():
    # Step 4: Evaluate MAE across 10 deterministic test cases against fuzzy targets
    test_inputs = [
        (15, 10), (25, 40), (45, 30), (50, 50), (60, 75),
        (75, 25), (85, 60), (90, 85), (95, 95), (30, 85)
    ]
    evaluations, abs_errors = [], []
    for h, p in test_inputs:
        true_fuzz = fuzzy_urgency(h, p)
        pred_dict = predict_response(h, p)
        err = round(abs(true_fuzz - pred_dict["urgency"]), 2)
        abs_errors.append(err)
        evaluations.append({
            "hazard": h, "people": p,
            "fuzzy_truth": true_fuzz,
            "neural_pred": pred_dict["urgency"],
            "error": err,
            "response_level": pred_dict["level"]
        })
    mae = round(float(np.mean(abs_errors)), 2)
    return mae, evaluations

def run_demo(hazard=80, people=70):
    # Step 5: Demo runner returning prediction, test evaluations and MAE
    mae, test_results = evaluate_test_cases()
    single_pred = predict_response(hazard, people)
    return {
        "lab": "Lab 08: Neuro-Fuzzy Hybrid Urgency",
        "status": "success",
        "sample_prediction": single_pred,
        "mae_score": mae,
        "evaluations": test_results,
        "architecture": "MinMaxScaler + MLPRegressor(hidden_layer_sizes=(8, 8))",
        "viva_insight": "A neural network approximates the non-linear fuzzy surface, learning from past logs while preserving interpretable linguistic bounds."
    }

if __name__ == "__main__":
    import json
    print(json.dumps(run_demo(), indent=2))
