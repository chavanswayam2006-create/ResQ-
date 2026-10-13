# ResQ-Grid — An AI & Soft-Computing Emergency Response Simulator

ResQ-Grid is an educational emergency dispatch simulator designed for laboratory practicals and viva voce examinations. During natural disasters (floods, structural fires, and multi-casualty incidents), control rooms must rapidly evaluate urgency, assign appropriate response units, and plan optimal routes through blocked roads and flooded city streets.

ResQ-Grid simulates an 8x8 urban grid where an autonomous AI dispatcher determines urgency (neuro-fuzzy regression), selects the optimal unit (Prolog Horn clauses), routes via cost-aware pathfinding (A* and BFS), and coordinates sector defense strategy (Minimax). Ten interactive "Lab" pages execute every AI and Soft-Computing technique independently with live Chart.js visualizations.

---

## 🛠️ Simplicity Guarantees & Tech Stack
- **Python 3.10+ & Flask**: Clean backend routes only, no database, no authentication, no Docker.
- **Frontend**: Pure HTML5, CSS3, Vanilla JavaScript, Chart.js (CDN). No React or build steps.
- **AI Libraries**: `numpy`, `scikit-fuzzy`, `scikit-learn`. (Note: Built-in numpy fallbacks are included for portability across Python versions).
- **Determinism**: Fixed random seed `42` ensures identical, repeatable results for viva demonstrations.
- **Viva-Ready**: Every lab file in `labs/` is strictly $\le 150$ lines with English comments on every step.

---

## 🚀 Quickstart Guide

1. **Clone or Navigate to the Project Root**:
   ```bash
   cd "ResQ AI"
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Launch the Application**:
   ```bash
   python app.py
   ```

4. **Open in Browser**:
   Navigate to [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 📂 Project Directory Structure

```text
ResQ AI/
├── app.py                      # Flask routes and REST API endpoints
├── requirements.txt            # Minimal dependencies (flask, numpy, scikit-fuzzy, scikit-learn)
├── README.md                   # Setup guide and project documentation
├── data/
│   ├── city.json               # 8x8 city topography, transit costs, and unit depots
│   ├── knowledge_base.pl       # Prolog Horn clauses & emergency dispatch facts
│   ├── corpus.txt              # 60 realistic radio dispatch training messages
│   └── incidents_history.csv   # Synthetic fuzzy training dataset (Lab 08)
├── labs/                       # 10 standalone lab modules (<= 150 lines each)
│   ├── lab01_peas.py           # PEAS specification & problem formulation
│   ├── lab02_prolog.py         # Horn clause logic deduction mirror
│   ├── lab03_search.py         # BFS (FIFO) vs DFS (LIFO) city grid scout
│   ├── lab04_astar.py          # A* cost-aware grid router & 8-puzzle solver
│   ├── lab05_minimax.py        # Minimax sector defense with alpha-beta pruning
│   ├── lab06_fuzzy.py          # Mamdani fuzzy logic urgency controller
│   ├── lab07_sugeno.py         # Sugeno weighted-average vs Mamdani centroid
│   ├── lab08_neuro_fuzzy.py    # MLPRegressor trained on fuzzy history
│   ├── lab09_neural_learning.py# Scratch numpy Perceptron & Winner-Takes-All clustering
│   └── lab10_language_model.py # Bigram & Trigram Markov autocomplete
├── sim/
│   ├── city.py                 # 8x8 grid state, unit tracking, and simulation clock
│   └── pipeline.py             # Autonomous AI reasoning and dispatch pipeline
├── templates/
│   ├── base.html               # Master layout, control room sidebar, & theme
│   ├── command_center.html     # Live 8x8 map, priority queue, and AI decision log
│   ├── intake.html             # Incident intake with NLP autocomplete & dispatch
│   ├── labs.html               # 10-Lab catalog cards
│   └── lab.html                # Universal interactive lab runner
├── static/
│   ├── style.css               # Control room design system (#0B1220 base)
│   └── app.js                  # Frontend map rendering, unit animation & Chart.js
├── design/
│   ├── generate_design.mjs     # Stitch SDK generation script
│   ├── command_center.html     # Design mockups
│   ├── intake.html
│   ├── lab_hub.html
│   └── lab_detail.html
└── docs/
    └── LAB_MAP.md              # University viva syllabus table & 30 Q&A pairs
```

---

## 🧪 The 10 Laboratory Modules

| Lab | Module Name | Implementation File | Key AI Concept |
|---|---|---|---|
| **01** | PEAS Agent | [`labs/lab01_peas.py`](file:///labs/lab01_peas.py) | Performance, Environment, Actuators, Sensors, State-Space formulation |
| **02** | Prolog Rule Brain | [`labs/lab02_prolog.py`](file:///labs/lab02_prolog.py) | Horn clauses, backward chaining unification, KB facts |
| **03** | BFS & DFS Scout | [`labs/lab03_search.py`](file:///labs/lab03_search.py) | Uninformed search, FIFO queue optimality vs LIFO stack exploration |
| **04** | A* Router & Puzzle | [`labs/lab04_astar.py`](file:///labs/lab04_astar.py) | Manhattan heuristic admissibility, cost-aware terrain ($f=g+h$), 8-puzzle |
| **05** | Minimax Strategy | [`labs/lab05_minimax.py`](file:///labs/lab05_minimax.py) | Adversarial game tree, alpha-beta pruning, multi-incident sector defense |
| **06** | Fuzzy Urgency | [`labs/lab06_fuzzy.py`](file:///labs/lab06_fuzzy.py) | Mamdani inference, triangular membership functions, centroid defuzzification |
| **07** | Mamdani vs Sugeno | [`labs/lab07_sugeno.py`](file:///labs/lab07_sugeno.py) | 0th-order Sugeno weighted average vs continuous centroid integration |
| **08** | Neuro-Fuzzy Hybrid | [`labs/lab08_neuro_fuzzy.py`](file:///labs/lab08_neuro_fuzzy.py) | MLPRegressor learning from fuzzy logs, output clamping, MAE evaluation |
| **09** | Neural Learning Rules | [`labs/lab09_neural_learning.py`](file:///labs/lab09_neural_learning.py) | Scratch Perceptron error-correction, Winner-Takes-All competitive clustering |
| **10** | Statistical Language Model | [`labs/lab10_language_model.py`](file:///labs/lab10_language_model.py) | N-gram Markov assumption, Bigram/Trigram transition probabilities, backoff |

*For complete examiner viva questions, consult [`docs/LAB_MAP.md`](file:///docs/LAB_MAP.md).*

---

## 🤖 The Autonomous Dispatch Pipeline (`sim/pipeline.py`)

When an incident report is submitted via the **Incident Intake** view (`/intake`):
1. **Keyword Analysis**: Maps report text to incident type (`fire`, `flood`, or `medical`).
2. **Urgency Prediction**: Computes continuous urgency score via the **Neuro-Fuzzy Hybrid** (Lab 08), supplemented by Mamdani (Lab 06) and Sugeno (Lab 07).
3. **Criticality Classification**: Evaluates if incident is `CRITICAL` or `ROUTINE` using the scratch **Perceptron** (Lab 09).
4. **Unit Eligibility & Allocation**: Deduces eligible units via **Prolog Horn Clauses** (Lab 02) and selects the closest available unit using **A* Cost-Aware Navigation** (Lab 04).
5. **Route Comparison**: Computes **BFS Unweighted Hops** (Lab 03) alongside A* to demonstrate why terrain cost awareness matters.
6. **Adversarial Sector Defense**: When multiple emergencies are open, **Minimax** (Lab 05) advises which sector must be fortified first.
7. **Simulation Clock**: Units advance along their computed path tile-by-tile on each simulation step (`POST /api/sim/step`), resolving incidents upon arrival.

---

## 🔬 Acceptance Criteria Verification

- [x] All 10 lab pages load and execute with real-time output and Chart.js graphs.
- [x] Incident Intake evaluates urgency, criticality flag, chosen unit, A* route cost, and BFS hop count.
- [x] Simulator executes 10 steps deterministically with seed 42.
- [x] Every lab file in `labs/` is strictly $\le 150$ lines with English comments on every step.
- [x] No complex setup or database required: only `pip install -r requirements.txt` and `python app.py`.
