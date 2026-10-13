"""
Lab 08: Neuro-Fuzzy Hybrid Urgency Predictor
Simplicity: MLPRegressor trained on Mamdani dataset with fuzzy level labeling.
"""
import os, warnings, numpy as np, pandas as pd
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import MinMaxScaler
from labs.lab06_fuzzy import fuzzy_urgency
warnings.filterwarnings("ignore")

CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "incidents_history.csv")

def ensure_dataset():
    # Step 1: Generate ~300 synthetic past incident records with seed 42
    if os.path.exists(CSV_PATH):
        return pd.read_csv(CSV_PATH)
    rng = np.random.RandomState(42)
    hazards = rng.uniform(0, 100, 300)
    peoples = rng.uniform(0, 100, 300)
    noise = rng.normal(0, 2.0, 300)
    urgencies = [float(np.clip(fuzzy_urgency(h, p) + n, 0.0, 100.0)) 
                 for h, p, n in zip(hazards, peoples, noise)]
    df = pd.DataFrame({
        "hazard_intensity": np.round(hazards, 2),
        "people_at_risk": np.round(peoples, 2),
        "urgency": np.round(urgencies, 2)
    })
    os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)
    df.to_csv(CSV_PATH, index=False)
    return df

# Step 2: Initialize scaler and train MLP neural network
_df = ensure_dataset()
_scaler = MinMaxScaler()
_X = _scaler.fit_transform(_df[["hazard_intensity", "people_at_risk"]].values)
_y = _df["urgency"].values

_mlp = MLPRegressor(hidden_layer_sizes=(8, 8), max_iter=600, random_state=42)
_mlp.fit(_X, _y)

def predict_response(hazard, people):
    # Step 3: Predict urgency and apply fuzzy linguistic labeling (clamped 0-100)
    h_val = float(np.clip(hazard, 0, 100))
    p_val = float(np.clip(people, 0, 100))
    x_scaled = _scaler.transform([[h_val, p_val]])
    pred = float(np.clip(_mlp.predict(x_scaled)[0], 0.0, 100.0))
    pred = round(pred, 2)
    level = "Low" if pred < 40.0 else ("Medium" if pred < 70.0 else "High")
    return {"urgency": pred, "level": level, "hazard": h_val, "people": p_val}

def evaluate_test_cases():
    # Step 4: Evaluate MAE across 10 deterministic test cases against fuzzy targets
    test_inputs = [
        (15, 10), (25, 40), (45, 30), (50, 50), (60, 75),
        (75, 25), (85, 60), (90, 85), (95, 95), (30, 85)
    ]
    evaluations = []
    abs_errors = []
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
