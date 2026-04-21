/* ============================================================
   My Food – app.js
   Restored Logic for Vibrant Energy Theme
   ============================================================ */

"use strict";

const CONDITION_TARGETS = {
  general: { calories: 2200, protein: 150, carbs: 325, fats: 78, label: "General Health" },
  weight_loss: { calories: 1600, protein: 120, carbs: 180, fats: 55, label: "Weight Loss" },
  diabetes: { calories: 2000, protein: 120, carbs: 195, fats: 70, label: "Diabetes" },
  high_bp: { calories: 2000, protein: 120, carbs: 300, fats: 55, label: "High BP" },
};

const FOOD_SUGGESTIONS = [
  "rice", "roti", "bread", "egg", "chicken", "fish", "dal", "sambar", "paneer", "rajma", "chickpeas",
  "milk", "curd", "apple", "banana", "orange", "mango", "grapes", "watermelon", "salad", "spinach",
  "broccoli", "carrot", "tomato", "potato", "pizza", "burger", "fries", "samosa", "biscuit", "chocolate",
  "coffee", "tea", "green tea", "juice", "soda", "water"
];

let state = {
  condition: "general",
  daily: { calories: 0, protein: 0, carbs: 0, fats: 0 },
  entries: [],
  entryCount: 0
};

const $ = id => document.getElementById(id);

document.addEventListener("DOMContentLoaded", () => {
  setDateLabels();
  initConditionButtons();
  initInputListeners();
  loadDailySummary();
  loadWeeklySummary();
  restoreCondition();
});

function setDateLabels() {
  const now = new Date();
  const opts = { weekday: "long", month: "long", day: "numeric" };
  $("header-date").textContent = now.toLocaleDateString("en-IN", opts);
}

function initConditionButtons() {
  document.querySelectorAll(".cond-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const cond = btn.dataset.cond;
      setCondition(cond);
      fetch("/api/set_condition", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ condition: cond })
      });
    });
  });
}

function setCondition(cond) {
  state.condition = cond;
  document.querySelectorAll(".cond-btn").forEach(b => b.classList.remove("active"));
  const activeBtn = $("cond-" + cond);
  if (activeBtn) activeBtn.classList.add("active");

  const target = CONDITION_TARGETS[cond] || CONDITION_TARGETS.general;
  $("active-condition-label").textContent = target.label;
  $("calTarget").textContent = target.calories;
  updateDailyBars(state.daily);
  localStorage.setItem("myfood_condition", cond);
}

function restoreCondition() {
  const saved = localStorage.getItem("myfood_condition") || "general";
  setCondition(saved);
}

function initInputListeners() {
  $("btnBefore").addEventListener("click", () => submitFood("before"));
  $("btnAfter").addEventListener("click", () => submitFood("after"));
  $("foodInput").addEventListener("input", handleAutocomplete);
  $("btnClearToday").addEventListener("click", clearToday);
}

function handleAutocomplete() {
  const val = $("foodInput").value.toLowerCase().trim();
  const list = $("autocompleteList");
  if (val.length < 2) { list.classList.add("hidden"); return; }

  const matches = FOOD_SUGGESTIONS.filter(f => f.includes(val)).slice(0, 5);
  if (!matches.length) { list.classList.add("hidden"); return; }

  list.innerHTML = matches.map(m => `<div class="ac-item" onclick="selectFood('${m}')">${m}</div>`).join("");
  list.classList.remove("hidden");
}

window.selectFood = function (val) {
  $("foodInput").value = val;
  $("autocompleteList").classList.add("hidden");
};

async function submitFood(mode) {
  const food = $("foodInput").value.trim();
  if (!food) return;

  const portion = parseFloat($("portionInput").value) || 1.0;
  const endpoint = mode === "before" ? "/api/analyze" : "/api/log";

  try {
    const res = await fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ food, portion, health_condition: state.condition })
    });
    const data = await res.json();

    if (!res.ok) { alert(data.error); return; }

    renderResult(data, mode);

    if (mode === "after") {
      loadDailySummary();
      loadWeeklySummary();
      $("foodInput").value = "";
    }
  } catch (err) {
    console.error(err);
  }
}

function renderResult(data, mode) {
  const rec = data.recommendation || {};
  const nutrition = data.nutrition || {};
  const severity = rec.severity || "green";

  $("resultPanel").classList.remove("hidden");
  $("resultFoodName").textContent = capitalize(data.food);
  $("resultModeBadge").textContent = mode === "before" ? "Pre-Analysis" : "Logged";

  const score = rec.health_score ?? 0;
  $("scoreNum").textContent = score.toFixed(1);
  $("scoreNum").style.color = score >= 7 ? "#38b000" : score >= 4 ? "#ffb703" : "#e63946";

  $("warningList").innerHTML = (rec.warnings || []).map(w => `<li class="li-warning">⚠️ ${w}</li>`).join("");
  $("positiveList").innerHTML = (rec.positives || []).map(p => `<li class="li-success">✅ ${p}</li>`).join("");
  $("tipList").innerHTML = (rec.tips || []).map(t => `<li class="li-tip">💡 ${t}</li>`).join("");

  $("resultPanel").scrollIntoView({ behavior: "smooth", block: "nearest" });
}

async function loadDailySummary() {
  const res = await fetch("/api/daily_summary");
  const data = await res.json();
  state.daily = data.totals || {};
  state.entryCount = data.entry_count || 0;
  state.entries = data.entries || [];

  $("calNum").textContent = Math.round(state.daily.calories || 0);
  $("calEntries").textContent = `${state.entryCount} item${state.entryCount !== 1 ? "s" : ""} logged`;
  updateDailyBars(state.daily);
  refreshLogList();
}

function updateDailyBars(totals) {
  const targets = CONDITION_TARGETS[state.condition] || CONDITION_TARGETS.general;

  const calPct = Math.min((totals.calories / targets.calories) * 100, 100);
  $("calCircle").style.width = calPct + "%";
  if (calPct > 100) $("calCircle").style.background = "#e63946";

  updateBar("barProtein", "valProtein", totals.protein, targets.protein, "g");
  updateBar("barCarbs", "valCarbs", totals.carbs, targets.carbs, "g");
  updateBar("barFats", "valFats", totals.fats, targets.fats, "g");
}

function updateBar(barId, valId, value, max, unit) {
  const pct = Math.min(((value || 0) / max) * 100, 100);
  $(barId).style.width = pct + "%";
  $(valId).textContent = (value || 0).toFixed(1) + unit;
}

function refreshLogList() {
  const card = $("logCard");
  if (!state.entries.length) { card.style.display = "none"; return; }
  card.style.display = "block";
  $("logList").innerHTML = state.entries.map(e => `
    <div class="log-item">
      <div class="log-info">
        <h5>${capitalize(e.food)}</h5>
        <span>${e.time}</span>
      </div>
      <div class="log-meta">${Math.round(e.nutrition.calories)} kcal</div>
    </div>
  `).reverse().join("");
}

async function loadWeeklySummary() {
  const res = await fetch("/api/weekly_summary");
  const data = await res.json();
  renderWeekBars(data.weekly || []);
}

function renderWeekBars(days) {
  const container = $("weekBars");
  const maxCal = Math.max(...days.map(d => d.totals.calories), 1000);

  container.innerHTML = days.map(d => {
    const pct = (d.totals.calories / maxCal) * 100;
    const isToday = d.date === new Date().toISOString().split("T")[0];
    return `
      <div style="flex:1; display:flex; flex-direction:column; align-items:center;">
        <div style="width:100%; height:${Math.max(pct, 5)}%; background:${isToday ? 'var(--primary)' : '#ddd'}; border-radius:4px;"></div>
        <span style="font-size:0.7rem; font-weight:700; margin-top:5px;">${d.day}</span>
      </div>
    `;
  }).join("");

  const tracked = days.filter(d => d.entry_count > 0).length;
  $("weekInsight").textContent = `${tracked}/7 days logged this week`;
}

async function clearToday() {
  if (!confirm("Clear today's logs?")) return;
  await fetch("/api/clear_today", { method: "POST" });
  loadDailySummary();
  $("resultPanel").classList.add("hidden");
}

function capitalize(s) { return s ? s.charAt(0).toUpperCase() + s.slice(1) : ""; }