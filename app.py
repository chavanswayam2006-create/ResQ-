"""
ResQ-Grid: Flask Application & REST API Routes
Simplicity: Pure Flask route handlers, no database, no authentication.
"""
from flask import Flask, render_template, request, jsonify
from sim.city import city_sim
from sim.pipeline import handle_incident
import labs.lab01_peas as lab01
import labs.lab02_prolog as lab02
import labs.lab03_search as lab03
import labs.lab04_astar as lab04
import labs.lab05_minimax as lab05
import labs.lab06_fuzzy as lab06
import labs.lab07_sugeno as lab07
import labs.lab08_neuro_fuzzy as lab08
import labs.lab09_neural_learning as lab09
import labs.lab10_language_model as lab10

app = Flask(__name__)

# Lab metadata registry for clean lab views and viva prep
LAB_METADATA = {
    1: {
        "num": "01",
        "title": "PEAS Agent & Problem Formulation",
        "subtitle": "Performance, Environment, Actuators, Sensors and Search Formalism",
        "aim": "To formulate an emergency response dispatch agent using the PEAS framework and define its initial state, goal criteria, transition actions, and terrain path costs.",
        "theory": "The PEAS model defines the agent's operating envelope: Performance (response time, lives saved, transit cost), Environment (8x8 disaster city with varying transit costs), Actuators (dispatch, move, reroute), and Sensors (radio reports, flood telemetry, GPS). Problem formulation defines the state space graph for deterministic search.",
        "module": lab01,
        "viva": [
            ("What does PEAS stand for in emergency management?", "Performance measure, Environment, Actuators, and Sensors."),
            ("Is the ResQ-Grid environment static or dynamic?", "Dynamic and partially observable, because floods expand, roads block, and new casualties appear in real time."),
            ("What represents the path cost in this agent formulation?", "The cumulative transit costs of traversed tiles: normal road (1), flood (5), and blocked debris (impassable).")
        ]
    },
    2: {
        "num": "02",
        "title": "Prolog Rule Brain & Knowledge Base",
        "subtitle": "First-Order Horn Clause Deduction for Resource Allocation",
        "aim": "To deduce suitable emergency vehicle assignments from knowledge base facts and Horn clause inference rules.",
        "theory": "Prolog represents knowledge declaratively using facts (unit/2, incident/3, needs/2) and rules (suitable(U,I) :- unit(U,T), incident(I,K,_), needs(K,T)). Inference proceeds via backward chaining unification to determine which units satisfy the logical constraints of an incident.",
        "module": lab02,
        "viva": [
            ("What is a Horn clause?", "A clause with at most one positive literal, written as Head :- Body in Prolog logic programming."),
            ("How does Prolog resolve suitable(U, I)?", "It unifies unit(U, T) with incident needs(K, T) through backward-chaining resolution."),
            ("Why is logic programming preferred for dispatch rules?", "Rules are declarative, auditable, and easily updated without altering procedural algorithms.")
        ]
    },
    3: {
        "num": "03",
        "title": "BFS & DFS Scout Search",
        "subtitle": "Uninformed Search Comparison on 8x8 Disaster Topography",
        "aim": "To compare Breadth-First Search (FIFO queue) and Depth-First Search (LIFO stack) in navigating around road obstructions.",
        "theory": "BFS explores nodes level-by-level, guaranteeing the shortest hop path in unweighted graphs with time complexity O(b^d). DFS dives deep along candidate paths, which requires less memory O(bm) but can produce long, suboptimal detours.",
        "module": lab03,
        "viva": [
            ("Why does BFS guarantee the shortest route here?", "In unweighted step costs, BFS explores all nodes at depth d before depth d+1."),
            ("When would DFS be disadvantageous for an emergency ambulance?", "DFS can wander along lengthy dead-end detours before backtracking, wasting vital response minutes."),
            ("What are the space complexities of BFS and DFS?", "BFS space complexity is O(b^d) (storing the entire queue frontier), whereas DFS is O(bm).")
        ]
    },
    4: {
        "num": "04",
        "title": "A* Router & 8-Puzzle Solver",
        "subtitle": "Informed Manhattan Search on Cost-Aware Grid & Sliding Tile",
        "aim": "To implement A* heuristic search (f = g + h) for cost-aware road traversal and 8-puzzle board reconfiguration.",
        "theory": "A* balances cost so far g(n) with estimated remaining cost h(n). For grid routing, the Manhattan distance h(n) = |dr| + |dc| is admissible (never overestimates) and consistent. For the 8-puzzle, Manhattan heuristic dominates misplaced tiles by expanding fewer nodes.",
        "module": lab04,
        "viva": [
            ("What condition guarantees A* optimality?", "An admissible heuristic (h(n) <= h*(n)) on trees, and consistency/monotonicity on graphs."),
            ("Why does A* prefer road tiles over flooded tiles?", "A* accounts for g(n); road cost is 1 while flood cost is 5, so A* detours around deep water when cheaper."),
            ("Why is Manhattan heuristic superior to Misplaced tiles in 8-puzzle?", "Manhattan distance provides a strictly higher or equal estimate, pruning more nodes without losing admissibility.")
        ]
    },
    5: {
        "num": "05",
        "title": "Minimax Adversarial Strategy Advisor",
        "subtitle": "Depth-Limited Game Tree Search for Sector Defense",
        "aim": "To prioritize city sectors under adversarial disaster expansion using minimax search with alpha-beta pruning.",
        "theory": "Disaster response can be modeled as a two-player zero-sum game: MAX (the responder) chooses which sector to reinforce, while MIN (the disaster) attacks vulnerable adjacent sectors. Utility calculates lives protected minus casualties.",
        "module": lab05,
        "viva": [
            ("What does the MAX player represent in this disaster formulation?", "The emergency command center aiming to maximize protected citizens."),
            ("How does alpha-beta pruning improve minimax efficiency?", "It prunes branches that are mathematically proven to be worse than previously evaluated moves, reducing effective branching factor."),
            ("Why is a depth limit (depth <= 4) applied?", "Real-time dispatch demands sub-second decisions, preventing exponential combinatorial explosion.")
        ]
    },
    6: {
        "num": "06",
        "title": "Fuzzy Logic Urgency Controller",
        "subtitle": "Mamdani Inference Controller with 9 IF-THEN Rules",
        "aim": "To construct a Mamdani fuzzy inference system evaluating hazard intensity and exposed population into an urgency score.",
        "theory": "Fuzzy logic models real-world vagueness using continuous membership degrees [0, 1]. Nine linguistic IF-THEN rules combine triangular memberships using the Min t-norm operator, defuzzifying with the Centroid method (center of gravity).",
        "module": lab06,
        "viva": [
            ("What is the advantage of fuzzy logic over crisp thresholding?", "It smoothly grades urgency; a hazard of 49 vs 51 does not abruptly switch dispatch behavior."),
            ("What is Mamdani defuzzification?", "The center of gravity (centroid) calculates the geometric balance point of the combined output fuzzy shape."),
            ("How many rules are evaluated in this 3x3 antecedent matrix?", "All 9 rules fire in parallel and their clipped consequences are unioned with the Max operator.")
        ]
    },
    7: {
        "num": "07",
        "title": "Mamdani vs Sugeno Defuzzification",
        "subtitle": "Comparative Benchmark of Centroid vs Weighted Average",
        "aim": "To evaluate differences between Mamdani continuous defuzzification and Sugeno singleton weighted-average calculation.",
        "theory": "Mamdani controllers use fuzzy output sets requiring numerical integration for defuzzification. Sugeno 0th-order controllers use crisp constant outputs (Low=20, Med=50, High=80) and compute defuzzification via weighted average, which is computationally lightweight.",
        "module": lab07,
        "viva": [
            ("Why is Sugeno defuzzification computationally faster than Mamdani?", "Sugeno avoids numerical area integration by using a single algebraic weighted average of crisp constants."),
            ("Which method is more natural for human expert explanation?", "Mamdani, because both antecedent and consequent use linguistic terms like 'Urgency is High'."),
            ("When would you pick Sugeno for an embedded emergency drone?", "Sugeno is ideal for microcontrollers with constrained processing power requiring fast real-time loops.")
        ]
    },
    8: {
        "num": "08",
        "title": "Neuro-Fuzzy Hybrid Urgency",
        "subtitle": "Multi-Layer Perceptron Regression Trained on Fuzzy Domain History",
        "aim": "To train an MLPRegressor on 300 synthetic fuzzy incidents and combine neural inference with fuzzy level labeling.",
        "theory": "Neuro-fuzzy systems combine the learning capability of neural networks with the interpretability of fuzzy logic. The MLP learns non-linear regression mappings directly from historical incident logs, while fuzzy thresholding clamps and classifies the output.",
        "module": lab08,
        "viva": [
            ("What is the role of the neural network in a neuro-fuzzy hybrid?", "The neural network learns and refines the non-linear relationship between inputs and urgency from empirical data."),
            ("Why is input scaling (MinMaxScaler) essential before MLP training?", "It ensures all features have equal dynamic range [0, 1], preventing dominant gradient updates and accelerating convergence."),
            ("How is the model performance evaluated?", "Using Mean Absolute Error (MAE) across test cases to measure average deviation from target urgency.")
        ]
    },
    9: {
        "num": "09",
        "title": "Neural Learning Rules from Scratch",
        "subtitle": "Perceptron Error-Correction and Competitive Winner-Takes-All",
        "aim": "To implement scratch numpy Perceptron classification and competitive unsupervised clustering.",
        "theory": "The Perceptron updates weights via the error-correction rule w <- w + eta*(y - y_hat)*x. In competitive learning, prototype neurons compete; the winner with highest dot product moves closer to the input pattern, clustering incidents into operational profiles.",
        "module": lab09,
        "viva": [
            ("What is the Perceptron learning rule?", "Weights are updated only upon error: w_new = w_old + eta * (target - output) * input."),
            ("Can a single-layer perceptron solve non-linearly separable problems?", "No, Perceptrons can only separate linearly separable classes (Minsky & Papert, 1969)."),
            ("What does Winner-Takes-All clustering achieve in emergency response?", "It automatically groups incoming calls into characteristic profiles (e.g., flash flood cluster, urban blaze cluster) without manual labels.")
        ]
    },
    10: {
        "num": "10",
        "title": "Statistical Language Models (SLM & uLM)",
        "subtitle": "Bigram and Trigram Markov Autocomplete for Radio Transcripts",
        "aim": "To construct Bigram and Trigram statistical language models for autocomplete suggestions and dispatch message generation.",
        "theory": "N-gram language models apply the Markov assumption: P(w_n | w_1...w_{n-1}) approx P(w_n | w_{n-k}...w_{n-1}). A bigram conditions on 1 previous word, while a trigram conditions on 2, estimating maximum likelihood probabilities via frequency counts.",
        "module": lab10,
        "viva": [
            ("What is the Markov assumption in N-gram language models?", "The probability of the current word depends only on the preceding (N-1) words, not the entire conversational history."),
            ("Why is trigram prediction better than bigram for dispatch radio?", "Trigrams carry dual-word context (e.g. 'fire truck' predicts 'dispatched' rather than just any verb after 'truck')."),
            ("How does backoff handle unseen word pairs?", "If a trigram is missing from the corpus, the model smoothly backs off to the bigram and then unigram frequencies.")
        ]
    }
}

# ----------------- PAGE ROUTES -----------------

@app.route("/")
def command_center():
    state = city_sim.get_state()
    return render_template("command_center.html", state=state)

@app.route("/intake")
def intake():
    state = city_sim.get_state()
    return render_template("intake.html", sectors=city_sim.sectors, state=state)

@app.route("/labs")
def labs_hub():
    return render_template("labs.html", labs=LAB_METADATA)

@app.route("/lab/<int:n>")
def lab_detail(n):
    if n not in LAB_METADATA:
        return "Lab not found", 404
    meta = LAB_METADATA[n]
    return render_template("lab.html", lab=meta, lab_id=n)

# ----------------- REST API ROUTES -----------------

@app.route("/api/sim/state", methods=["GET"])
def api_sim_state():
    return jsonify(city_sim.get_state())

@app.route("/api/sim/step", methods=["POST"])
def api_sim_step():
    new_state = city_sim.step()
    return jsonify({"status": "success", "state": new_state})

@app.route("/api/sim/reset", methods=["POST"])
def api_sim_reset():
    city_sim.reset()
    return jsonify({"status": "success", "state": city_sim.get_state()})

@app.route("/api/sim/incident", methods=["POST"])
def api_sim_incident():
    data = request.get_json() or {}
    text = data.get("text", "Emergency call received")
    sector = data.get("sector", "Sector A")
    hazard = float(data.get("hazard", 50))
    people = float(data.get("people", 50))
    result = handle_incident(text, sector, hazard, people)
    return jsonify(result)

@app.route("/api/next-word", methods=["POST"])
def api_next_word():
    data = request.get_json() or {}
    text = data.get("text", "")
    suggestions = lab10.predict_next(text, n=3)
    return jsonify({"suggestions": suggestions})

@app.route("/api/lab/<int:n>", methods=["POST"])
def api_run_lab(n):
    if n not in LAB_METADATA:
        return jsonify({"status": "error", "message": "Unknown lab index"}), 404
    
    data = request.get_json() or {}
    mod = LAB_METADATA[n]["module"]
    
    # Route custom inputs per lab if supplied
    try:
        if n == 1:
            res = mod.run_demo()
        elif n == 2:
            query = data.get("query", "suitable(U, fire)")
            res = mod.run_demo(query)
        elif n == 3:
            start = tuple(data.get("start", [1, 1]))
            goal = tuple(data.get("goal", [6, 6]))
            res = mod.run_demo(start, goal)
        elif n == 4:
            res = mod.run_demo()
        elif n == 5:
            res = mod.run_demo()
        elif n == 6:
            hazard = float(data.get("hazard", 75))
            people = float(data.get("people", 80))
            res = mod.run_demo(hazard, people)
        elif n == 7:
            res = mod.run_demo()
        elif n == 8:
            hazard = float(data.get("hazard", 80))
            people = float(data.get("people", 70))
            res = mod.run_demo(hazard, people)
        elif n == 9:
            sample = tuple(data.get("sample", [0.85, 0.75, 0.6]))
            res = mod.run_demo(sample)
        elif n == 10:
            seed = data.get("seed", "send fire")
            res = mod.run_demo(seed)
        else:
            res = mod.run_demo()
        return jsonify(res)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    print("ResQ-Grid Server running on http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=True)
