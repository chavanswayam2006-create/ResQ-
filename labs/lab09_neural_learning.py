"""
Lab 09: Scratch Neural Learning Rules (Perceptron & Competitive Winner-Takes-All)
Simplicity: Pure numpy implementation without third-party neural frameworks.
"""
import numpy as np

# Seed 42 for deterministic lab reproducibility
rng = np.random.RandomState(42)

# Step 1: Synthetic incident dataset [people_at_risk, spread_speed, road_difficulty] (0 to 1)
X_TRAIN = np.array([
    [0.1, 0.2, 0.1], [0.2, 0.1, 0.3], [0.3, 0.3, 0.2], [0.15, 0.25, 0.2], # Routine
    [0.8, 0.9, 0.7], [0.9, 0.7, 0.8], [0.75, 0.85, 0.6], [0.85, 0.95, 0.9], # Critical
    [0.2, 0.3, 0.1], [0.7, 0.8, 0.65], [0.3, 0.1, 0.4], [0.9, 0.8, 0.7]
])
# Labels: 0 = Routine, 1 = Critical
Y_TRAIN = np.array([0, 0, 0, 0, 1, 1, 1, 1, 0, 1, 0, 1])

# Step 2: Perceptron Training (Hebbian error-correction rule)
def train_perceptron(epochs=15, lr=0.1):
    weights = np.zeros(3)
    bias = 0.0
    epoch_errors = []
    
    for _ in range(epochs):
        errors = 0
        for x, target in zip(X_TRAIN, Y_TRAIN):
            activation = 1 if (np.dot(weights, x) + bias) >= 0.0 else 0
            err = target - activation
            if err != 0:
                weights += lr * err * x
                bias += lr * err
                errors += 1
        epoch_errors.append(errors)
    return weights, bias, epoch_errors

P_WEIGHTS, P_BIAS, P_ERRORS = train_perceptron()

def classify_critical(people_norm, spread_norm, access_norm):
    # Step 3: Perceptron inference function used by the simulator pipeline
    x = np.array([people_norm, spread_norm, access_norm])
    score = float(np.dot(P_WEIGHTS, x) + P_BIAS)
    is_crit = bool(score >= 0.0)
    return {"critical": is_crit, "label": "Critical" if is_crit else "Routine", "score": round(score, 3)}

# Step 4: Competitive Learning (Winner-Takes-All clustering for 3 incident patterns)
def train_competitive(k=3, epochs=25, alpha=0.15):
    # Initialize 3 normalized prototype weight vectors
    centers = rng.uniform(0.1, 0.9, (k, 3))
    centers /= np.linalg.norm(centers, axis=1, keepdims=True)
    
    for _ in range(epochs):
        for x in X_TRAIN:
            x_norm = x / (np.linalg.norm(x) + 1e-8)
            # Find winner (highest cosine similarity / dot product)
            winner = np.argmax(np.dot(centers, x_norm))
            # Winner takes all update
            centers[winner] += alpha * (x_norm - centers[winner])
            centers[winner] /= np.linalg.norm(centers[winner])
            
    # Assign cluster labels to training data
    cluster_assignments = [int(np.argmax(np.dot(centers, x / np.linalg.norm(x)))) for x in X_TRAIN]
    return centers, cluster_assignments

PROTOTYPES, CLUSTERS = train_competitive()

def run_demo(sample=(0.85, 0.75, 0.6)):
    # Step 5: Demo packaging with epoch errors and cluster patterns for charts
    pred = classify_critical(*sample)
    pattern_descriptions = {
        0: "Pattern 1: Low-hazard routine city calls (local minor trauma)",
        1: "Pattern 2: Rapidly spreading structural hazards (major fires)",
        2: "Pattern 3: Inundated dense access crisis (severe flood rescue)"
    }
    return {
        "lab": "Lab 09: Neural Learning Rules",
        "status": "success",
        "sample_input": list(sample),
        "perceptron_prediction": pred,
        "epoch_errors": P_ERRORS,
        "clusters": [
            {"point": list(x), "cluster": c, "desc": pattern_descriptions.get(c, "")}
            for x, c in zip(X_TRAIN, CLUSTERS)
        ],
        "viva_insight": "Perceptron adjusts weights proportionally to classification error, while Competitive Learning clusters patterns via unsupervised Winner-Takes-All."
    }

if __name__ == "__main__":
    import json
    print(json.dumps(run_demo(), indent=2))
