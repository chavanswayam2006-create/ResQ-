// ResQ-Grid Client-side Controller & Chart.js Integration
let autoRunTimer = null;
let activeChartInstance = null;

// Utility: Flash UI element or toast
function showNotice(msg) {
  console.log("[ResQ-Grid]", msg);
}

// ---------------- COMMAND CENTER ----------------
function initCommandCenter(initialState) {
  let state = initialState;
  const gridContainer = document.getElementById("grid-board");
  const queueContainer = document.getElementById("queue-container");
  const logContainer = document.getElementById("decision-log-list");
  const btnStep = document.getElementById("btn-step");
  const btnAuto = document.getElementById("btn-autorun");
  const btnReset = document.getElementById("btn-reset");
  const modalProfile = document.getElementById("profile-modal");

  function renderGrid() {
    if (!gridContainer || !state.grid) return;
    gridContainer.innerHTML = "";
    
    // Create map coordinate lookup for units and active routes
    const unitMap = {};
    const routeCoords = new Set();
    state.units.forEach(u => {
      unitMap[`${u.pos[0]},${u.pos[1]}`] = u;
      if (u.route && u.route.length > 0) {
        u.route.forEach(pt => routeCoords.add(`${pt[0]},${pt[1]}`));
      }
    });

    const incidentMap = {};
    state.incidents.filter(i => i.status !== "resolved").forEach(i => {
      incidentMap[`${i.target_pos[0]},${i.target_pos[1]}`] = i;
    });

    for (let r = 0; r < 8; r++) {
      for (let c = 0; c < 8; c++) {
        const cellType = state.grid[r][c];
        const cell = document.createElement("div");
        cell.className = `grid-cell cell-${cellType}`;
        cell.dataset.row = r;
        cell.dataset.col = c;
        cell.title = `(${r}, ${c}) ${cellType}`;

        const coordKey = `${r},${c}`;
        if (routeCoords.has(coordKey)) {
          cell.classList.add("path-highlight");
        }

        // Unit placement
        if (unitMap[coordKey]) {
          const u = unitMap[coordKey];
          const uMarker = document.createElement("div");
          uMarker.className = `unit-marker unit-${u.type}`;
          uMarker.textContent = u.id;
          uMarker.title = `${u.name} [${u.status.toUpperCase()}]`;
          cell.appendChild(uMarker);
        }

        // Incident marker
        if (incidentMap[coordKey]) {
          const inc = incidentMap[coordKey];
          const incIcon = document.createElement("div");
          incIcon.className = "incident-marker";
          incIcon.textContent = inc.type === "fire" ? "🔥" : (inc.type === "flood" ? "🌊" : "🏥");
          incIcon.title = `${inc.id}: ${inc.type.toUpperCase()} (Urgency: ${inc.urgency}%)`;
          cell.appendChild(incIcon);
        }

        gridContainer.appendChild(cell);
      }
    }
  }

  function renderQueue() {
    if (!queueContainer) return;
    queueContainer.innerHTML = "";
    if (state.incidents.length === 0) {
      queueContainer.innerHTML = `<div style="font-size: 0.8rem; color: var(--text-muted); padding: 1rem; text-align: center;">No active incidents. City is secure.</div>`;
      return;
    }

    state.incidents.forEach(inc => {
      const card = document.createElement("div");
      card.className = `queue-card ${inc.is_critical ? "critical" : "routine"}`;
      const color = inc.urgency > 70 ? "var(--accent-red)" : (inc.urgency > 40 ? "var(--accent-amber)" : "var(--accent-green)");
      card.innerHTML = `
        <div class="queue-card-top">
          <span class="queue-title">${inc.id}: ${inc.type.toUpperCase()}</span>
          <span class="queue-score" style="color: ${color};">${inc.urgency}%</span>
        </div>
        <div class="queue-meta">${inc.sector} • ${inc.status === "resolved" ? "✅ RESOLVED" : `Assigned: ${inc.assigned_unit || "Queue"}`}</div>
        <div class="urgency-progress">
          <div class="urgency-fill" style="width: ${inc.urgency}%; background: ${color};"></div>
        </div>
      `;
      queueContainer.appendChild(card);
    });
  }

  function renderLog() {
    if (!logContainer) return;
    logContainer.innerHTML = "";
    state.log.forEach(item => {
      const row = document.createElement("div");
      row.className = "log-row";
      row.innerHTML = `<span class="log-timestamp">[${item.time}]</span><span>${item.text}</span>`;
      logContainer.appendChild(row);
    });
  }

  function updateView(newState) {
    state = newState;
    renderGrid();
    renderQueue();
    renderLog();
  }

  // Simulator step action
  btnStep?.addEventListener("click", async () => {
    try {
      const res = await fetch("/api/sim/step", { method: "POST" });
      const data = await res.json();
      if (data.status === "success") updateView(data.state);
    } catch (err) {
      console.error("Step error:", err);
    }
  });

  // Simulator auto-run action
  btnAuto?.addEventListener("click", () => {
    if (autoRunTimer) {
      clearInterval(autoRunTimer);
      autoRunTimer = null;
      btnAuto.textContent = "Auto-run";
      btnAuto.classList.remove("btn-primary");
    } else {
      btnAuto.textContent = "Pause Auto";
      btnAuto.classList.add("btn-primary");
      autoRunTimer = setInterval(async () => {
        try {
          const res = await fetch("/api/sim/step", { method: "POST" });
          const data = await res.json();
          if (data.status === "success") updateView(data.state);
        } catch (e) {
          clearInterval(autoRunTimer);
          autoRunTimer = null;
        }
      }, 1200);
    }
  });

  // Simulator reset action
  btnReset?.addEventListener("click", async () => {
    if (autoRunTimer) {
      clearInterval(autoRunTimer);
      autoRunTimer = null;
      btnAuto.textContent = "Auto-run";
      btnAuto.classList.remove("btn-primary");
    }
    const res = await fetch("/api/sim/reset", { method: "POST" });
    const data = await res.json();
    if (data.status === "success") updateView(data.state);
  });

  // Profile modal triggers
  document.getElementById("btn-open-profile")?.addEventListener("click", () => {
    modalProfile?.classList.add("open");
  });
  document.getElementById("btn-close-profile")?.addEventListener("click", () => {
    modalProfile?.classList.remove("open");
  });

  renderGrid();
  renderQueue();
  renderLog();
}

// ---------------- INCIDENT INTAKE ----------------
function initIntake() {
  const txtArea = document.getElementById("report-text");
  const chipsTray = document.getElementById("chips-tray");
  const slHazard = document.getElementById("hazard-slider");
  const slPeople = document.getElementById("people-slider");
  const tagHazard = document.getElementById("hazard-val");
  const tagPeople = document.getElementById("people-val");
  const btnDispatch = document.getElementById("btn-dispatch");
  const resultsCard = document.getElementById("dispatch-results-card");

  slHazard?.addEventListener("input", (e) => { tagHazard.textContent = e.target.value; });
  slPeople?.addEventListener("input", (e) => { tagPeople.textContent = e.target.value; });

  let debounceTimer = null;
  async function fetchNextWords(text) {
    if (!chipsTray) return;
    try {
      const res = await fetch("/api/next-word", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text })
      });
      const data = await res.json();
      chipsTray.innerHTML = "";
      if (data.suggestions && data.suggestions.length > 0) {
        data.suggestions.forEach(s => {
          const chip = document.createElement("button");
          chip.className = "chip-btn";
          chip.type = "button";
          chip.textContent = `+ ${s.word} (${Math.round(s.prob * 100)}%)`;
          chip.addEventListener("click", () => {
            txtArea.value = (txtArea.value.trim() + " " + s.word).trim() + " ";
            txtArea.focus();
            fetchNextWords(txtArea.value);
          });
          chipsTray.appendChild(chip);
        });
      }
    } catch (e) {
      console.error("Autocomplete error:", e);
    }
  }

  txtArea?.addEventListener("input", (e) => {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => fetchNextWords(e.target.value), 250);
  });

  btnDispatch?.addEventListener("click", async () => {
    const text = txtArea.value.trim() || "Emergency report received";
    const sector = document.getElementById("sector-select").value;
    const hazard = parseFloat(slHazard.value);
    const people = parseFloat(slPeople.value);

    btnDispatch.disabled = true;
    btnDispatch.textContent = "Analyzing & Dispatching...";

    try {
      const res = await fetch("/api/sim/incident", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text, sector, hazard, people })
      });
      const data = await res.json();
      btnDispatch.disabled = false;
      btnDispatch.textContent = "Dispatch Response Unit";

      if (data.status === "success") {
        const inc = data.incident;
        if (resultsCard) {
          resultsCard.style.display = "flex";
          document.getElementById("res-badge-type").textContent = `${inc.type.toUpperCase()} INCIDENT`;
          const badgeCrit = document.getElementById("res-badge-critical");
          badgeCrit.textContent = inc.is_critical ? "CRITICAL (PERCEPTRON)" : "ROUTINE (PERCEPTRON)";
          badgeCrit.style.background = inc.is_critical ? "rgba(239, 68, 68, 0.2)" : "rgba(34, 211, 238, 0.2)";
          badgeCrit.style.color = inc.is_critical ? "var(--accent-red)" : "var(--accent-cyan)";

          document.getElementById("res-urgency-val").textContent = `${inc.urgency}%`;
          document.getElementById("res-unit-val").textContent = `${inc.assigned_unit} (${inc.assigned_unit_name})`;
          document.getElementById("res-astar-val").textContent = `${inc.astar_hops} Hops (Cost ${inc.astar_cost})`;
          document.getElementById("res-bfs-val").textContent = `${inc.bfs_hops} Hops (Unweighted)`;
          document.getElementById("res-minimax-desc").textContent = 
            `Minimax Strategy recommends fortifying ${inc.minimax_priority_sector} first to prevent casualty spread.`;
        }
      }
    } catch (err) {
      console.error(err);
      btnDispatch.disabled = false;
      btnDispatch.textContent = "Dispatch Response Unit";
    }
  });

  // Pre-populate initial suggestions
  fetchNextWords(txtArea?.value || "fire");
}

// ---------------- UNIVERSAL LAB RUNNER ----------------
function initLabRunner(labId) {
  const btnRun = document.getElementById("btn-run-lab");
  const chartCanvas = document.getElementById("labChart");
  const tableContainer = document.getElementById("results-table-container");

  btnRun?.addEventListener("click", async () => {
    btnRun.disabled = true;
    btnRun.textContent = "Running Algorithm...";
    try {
      const payload = collectLabInputs(labId);
      const res = await fetch(`/api/lab/${labId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      btnRun.disabled = false;
      btnRun.textContent = "Run Lab Demo";

      if (data.status === "success") {
        renderLabResults(labId, data, chartCanvas, tableContainer);
      }
    } catch (err) {
      console.error(err);
      btnRun.disabled = false;
      btnRun.textContent = "Run Lab Demo";
    }
  });

  // Run automatically once on page load for immediate feedback
  btnRun?.click();
}

function collectLabInputs(labId) {
  if (labId === 2) {
    const q = document.getElementById("inp-query")?.value;
    return q ? { query: q } : {};
  }
  if (labId === 6 || labId === 8) {
    const h = document.getElementById("inp-hazard")?.value;
    const p = document.getElementById("inp-people")?.value;
    return { hazard: h || 75, people: p || 80 };
  }
  if (labId === 10) {
    const seed = document.getElementById("inp-seed")?.value;
    return seed ? { seed } : {};
  }
  return {};
}

function renderLabResults(labId, data, canvas, tableBox) {
  if (activeChartInstance) {
    activeChartInstance.destroy();
    activeChartInstance = null;
  }

  const ctx = canvas?.getContext("2d");
  if (!ctx) return;

  // Lab-specific chart and tabular rendering
  if (labId === 1) {
    // PEAS Table display
    tableBox.innerHTML = `
      <table style="width: 100%; font-size: 0.85rem; border-collapse: collapse;">
        <thead><tr><th style="padding: 0.5rem; text-align: left;">PEAS Dimension</th><th style="padding: 0.5rem; text-align: left;">Agent Specification</th></tr></thead>
        <tbody>
          <tr><td style="padding: 0.5rem; color: var(--accent-cyan);">Performance</td><td style="padding: 0.5rem;">Response time, Lives saved, Fuel/damage cost</td></tr>
          <tr><td style="padding: 0.5rem; color: var(--accent-cyan);">Environment</td><td style="padding: 0.5rem;">8x8 city grid, floods (5), debris (inf), dynamic incidents</td></tr>
          <tr><td style="padding: 0.5rem; color: var(--accent-cyan);">Actuators</td><td style="padding: 0.5rem;">dispatch_unit, move_unit, reroute_unit</td></tr>
          <tr><td style="padding: 0.5rem; color: var(--accent-cyan);">Sensors</td><td style="padding: 0.5rem;">Incident text reports, flood water level, GPS coordinates</td></tr>
        </tbody>
      </table>
    `;
    activeChartInstance = new Chart(ctx, {
      type: "radar",
      data: {
        labels: ["Response Time", "Lives Saved", "Cost Efficiency", "Route Precision", "Constraint Safety"],
        datasets: [{
          label: "Agent Utility Profile",
          data: [92, 95, 85, 90, 98],
          backgroundColor: "rgba(34, 211, 238, 0.2)",
          borderColor: "#22D3EE",
          pointBackgroundColor: "#22D3EE"
        }]
      },
      options: { scales: { r: { min: 0, max: 100, grid: { color: "rgba(255,255,255,0.08)" } } } }
    });
  } else if (labId === 2) {
    // Prolog Side-by-Side viewer
    tableBox.innerHTML = `
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
        <div>
          <div style="font-size: 0.75rem; color: var(--text-muted); margin-bottom: 0.3rem;">PROLOG KB (data/knowledge_base.pl)</div>
          <pre style="background: #080E18; padding: 0.75rem; font-size: 0.75rem; border-radius: 6px; overflow-x: auto; color: #7DD3FC;">${data.prolog_code}</pre>
        </div>
        <div>
          <div style="font-size: 0.75rem; color: var(--text-muted); margin-bottom: 0.3rem;">UNIFIED QUERY RESULTS</div>
          <pre style="background: #080E18; padding: 0.75rem; font-size: 0.75rem; border-radius: 6px; overflow-x: auto; color: #86EFAC;">${JSON.stringify(data.results, null, 2)}</pre>
        </div>
      </div>
    `;
    activeChartInstance = new Chart(ctx, {
      type: "bar",
      data: {
        labels: data.results.map(r => r.unit || r.incident_kind),
        datasets: [{
          label: "Binding Confidence",
          data: data.results.map(() => 100),
          backgroundColor: "#22C55E"
        }]
      },
      options: { scales: { y: { min: 0, max: 100 } } }
    });
  } else if (labId === 3) {
    // BFS vs DFS comparison
    const cmp = data.comparison;
    tableBox.innerHTML = `
      <table style="width: 100%; font-size: 0.85rem; border-collapse: collapse;">
        <thead><tr><th style="padding: 0.5rem; text-align: left;">Search Algorithm</th><th style="padding: 0.5rem;">Path Length (Tiles)</th><th style="padding: 0.5rem;">Nodes Explored</th><th style="padding: 0.5rem;">Optimality</th></tr></thead>
        <tbody>
          <tr><td style="padding: 0.5rem; color: var(--accent-cyan);">BFS (FIFO Queue)</td><td style="padding: 0.5rem; text-align: center;">${cmp.bfs_path_length}</td><td style="padding: 0.5rem; text-align: center;">${cmp.bfs_nodes_explored}</td><td style="padding: 0.5rem;">Optimal Shortest Hops</td></tr>
          <tr><td style="padding: 0.5rem; color: var(--accent-amber);">DFS (LIFO Stack)</td><td style="padding: 0.5rem; text-align: center;">${cmp.dfs_path_length}</td><td style="padding: 0.5rem; text-align: center;">${cmp.dfs_nodes_explored}</td><td style="padding: 0.5rem;">Suboptimal Detour</td></tr>
        </tbody>
      </table>
    `;
    activeChartInstance = new Chart(ctx, {
      type: "bar",
      data: {
        labels: ["Path Length (Hops)", "Nodes Explored"],
        datasets: [
          { label: "BFS", data: [cmp.bfs_path_length, cmp.bfs_nodes_explored], backgroundColor: "#22D3EE" },
          { label: "DFS", data: [cmp.dfs_path_length, cmp.dfs_nodes_explored], backgroundColor: "#F59E0B" }
        ]
      }
    });
  } else if (labId === 4) {
    // A* Grid & 8-Puzzle
    const puz = data.puzzle_8;
    tableBox.innerHTML = `
      <div style="font-size: 0.85rem; line-height: 1.5;">
        <div><strong>Grid A* Path Cost:</strong> ${data.grid_navigation.cost} (Explored: ${data.grid_navigation.nodes_explored} nodes)</div>
        <div><strong>8-Puzzle Manhattan:</strong> ${puz.manhattan_solution.moves} moves (${puz.manhattan_solution.nodes_expanded} nodes expanded)</div>
        <div><strong>8-Puzzle Misplaced:</strong> ${puz.misplaced_solution.moves} moves (${puz.misplaced_solution.nodes_expanded} nodes expanded)</div>
      </div>
    `;
    activeChartInstance = new Chart(ctx, {
      type: "bar",
      data: {
        labels: ["Manhattan Heuristic", "Misplaced Tiles"],
        datasets: [{
          label: "Nodes Expanded to Goal",
          data: [puz.manhattan_solution.nodes_expanded, puz.misplaced_solution.nodes_expanded],
          backgroundColor: ["#22D3EE", "#EF4444"]
        }]
      }
    });
  } else if (labId === 5) {
    // Minimax strategy
    const pops = data.sector_populations;
    tableBox.innerHTML = `
      <div style="font-size: 0.85rem;">
        <div><strong>Adversarial Scenario:</strong> ${data.scenario}</div>
        <div><strong>MAX Selected Defense:</strong> <span style="color: var(--accent-cyan); font-weight: 700;">${data.best_move}</span> (Projected Saved Utility: ${data.projected_utility_score})</div>
      </div>
    `;
    activeChartInstance = new Chart(ctx, {
      type: "bar",
      data: {
        labels: Object.keys(pops),
        datasets: [{
          label: "Population at Risk",
          data: Object.values(pops),
          backgroundColor: Object.keys(pops).map(s => s === data.best_move ? "#22C55E" : (s === "Sector E" ? "#EF4444" : "#1E293B"))
        }]
      }
    });
  } else if (labId === 6) {
    // Fuzzy membership functions
    const c = data.curves;
    tableBox.innerHTML = `
      <div style="font-size: 0.9rem;">
        Urgency Score: <strong style="color: var(--accent-red); font-size: 1.2rem;">${data.urgency_score}%</strong> (${data.linguistic_label} Priority)
      </div>
    `;
    activeChartInstance = new Chart(ctx, {
      type: "line",
      data: {
        labels: c.x,
        datasets: [
          { label: "Low Urgency", data: c.low, borderColor: "#22C55E", tension: 0.1 },
          { label: "Medium Urgency", data: c.med, borderColor: "#F59E0B", tension: 0.1 },
          { label: "High Urgency", data: c.high, borderColor: "#EF4444", tension: 0.1 }
        ]
      }
    });
  } else if (labId === 7) {
    // Mamdani vs Sugeno
    const rows = data.comparison_table.map(r => 
      `<tr><td style="padding: 0.4rem;">(${r.hazard}, ${r.people})</td><td style="padding: 0.4rem;">${r.mamdani}%</td><td style="padding: 0.4rem;">${r.sugeno}%</td><td style="padding: 0.4rem; color: var(--accent-cyan);">${r.abs_diff}%</td></tr>`
    ).join("");
    tableBox.innerHTML = `
      <table style="width: 100%; font-size: 0.85rem; border-collapse: collapse;">
        <thead><tr><th style="padding: 0.4rem; text-align: left;">Case (H, P)</th><th style="padding: 0.4rem;">Mamdani</th><th style="padding: 0.4rem;">Sugeno</th><th style="padding: 0.4rem;">Abs Diff</th></tr></thead>
        <tbody>${rows}</tbody>
      </table>
    `;
    activeChartInstance = new Chart(ctx, {
      type: "bar",
      data: {
        labels: data.comparison_table.map((_, i) => `Case ${i+1}`),
        datasets: [
          { label: "Mamdani Centroid", data: data.comparison_table.map(r => r.mamdani), backgroundColor: "#22D3EE" },
          { label: "Sugeno Weighted Avg", data: data.comparison_table.map(r => r.sugeno), backgroundColor: "#F59E0B" }
        ]
      }
    });
  } else if (labId === 8) {
    // Neuro-Fuzzy
    const rows = data.evaluations.map(e => 
      `<tr><td style="padding: 0.35rem;">(${e.hazard}, ${e.people})</td><td style="padding: 0.35rem;">${e.fuzzy_truth}%</td><td style="padding: 0.35rem;">${e.neural_pred}%</td><td style="padding: 0.35rem;">${e.error}%</td><td style="padding: 0.35rem;">${e.response_level}</td></tr>`
    ).join("");
    tableBox.innerHTML = `
      <div style="margin-bottom: 0.5rem; font-size: 0.85rem;"><strong>Model:</strong> ${data.architecture} | <strong>Evaluation MAE:</strong> <span style="color: var(--accent-cyan); font-weight: 700;">${data.mae_score}%</span></div>
      <table style="width: 100%; font-size: 0.8rem; border-collapse: collapse;">
        <thead><tr><th style="padding: 0.35rem; text-align: left;">Input</th><th style="padding: 0.35rem;">Fuzzy Ground Truth</th><th style="padding: 0.35rem;">MLP Prediction</th><th style="padding: 0.35rem;">Error</th><th style="padding: 0.35rem;">Level</th></tr></thead>
        <tbody>${rows}</tbody>
      </table>
    `;
    activeChartInstance = new Chart(ctx, {
      type: "line",
      data: {
        labels: data.evaluations.map((_, i) => `#${i+1}`),
        datasets: [
          { label: "Fuzzy Truth", data: data.evaluations.map(e => e.fuzzy_truth), borderColor: "#22C55E", tension: 0.2 },
          { label: "MLP Neural Urgency", data: data.evaluations.map(e => e.neural_pred), borderColor: "#EF4444", borderDash: [4, 4], tension: 0.2 }
        ]
      }
    });
  } else if (labId === 9) {
    // Scratch Neural Learning
    tableBox.innerHTML = `
      <div style="font-size: 0.85rem;">
        <div><strong>Sample Evaluation:</strong> Criticality = <span style="color: var(--accent-red); font-weight: 700;">${data.perceptron_prediction.label}</span> (Score: ${data.perceptron_prediction.score})</div>
        <div style="margin-top: 0.5rem;"><strong>Unsupervised Patterns (Winner-Takes-All):</strong></div>
        <ul style="margin-left: 1rem; margin-top: 0.25rem;">
          <li>Pattern 1: Low-hazard routine calls</li>
          <li>Pattern 2: Rapid spreading structural blazes</li>
          <li>Pattern 3: Dense access inundation / water crisis</li>
        </ul>
      </div>
    `;
    activeChartInstance = new Chart(ctx, {
      type: "line",
      data: {
        labels: data.epoch_errors.map((_, i) => `Epoch ${i+1}`),
        datasets: [{
          label: "Perceptron Misclassifications",
          data: data.epoch_errors,
          borderColor: "#22D3EE",
          backgroundColor: "rgba(34, 211, 238, 0.1)",
          fill: true
        }]
      }
    });
  } else if (labId === 10) {
    // Language model
    const sugs = data.autocomplete_suggestions;
    tableBox.innerHTML = `
      <div style="font-size: 0.85rem;">
        <div><strong>Seed Phrase:</strong> "${data.seed_phrase}"</div>
        <div style="margin-top: 0.3rem;"><strong>Autonomously Generated Dispatch Alert:</strong></div>
        <blockquote style="margin: 0.5rem 0; padding: 0.5rem 0.75rem; background: #080E18; border-left: 3px solid var(--accent-cyan); font-family: 'JetBrains Mono', monospace; color: #7DD3FC;">"${data.generated_dispatch_message}"</blockquote>
        <div>Corpus Tokens: ${data.corpus_tokens_count} | Unique Vocab: ${data.unique_vocab_size}</div>
      </div>
    `;
    activeChartInstance = new Chart(ctx, {
      type: "bar",
      data: {
        labels: sugs.map(s => s.word),
        datasets: [{
          label: "Next Token Transition Probability",
          data: sugs.map(s => Math.round(s.prob * 100)),
          backgroundColor: "#22C55E"
        }]
      },
      options: { scales: { y: { min: 0, max: 100 } } }
    });
  }
}
