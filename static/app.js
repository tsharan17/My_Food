/* ============================================================
   NutriGuard – app.js
   Handles all UI interactions, API calls, and dynamic updates
   ============================================================ */

"use strict";

// ─────────────────────────────────────────────
// Constants & State
// ─────────────────────────────────────────────
const CONDITION_TARGETS = {
  general:     { calories: 2200, protein: 150, carbs: 325, fats: 78, fiber: 38, sugar: 50,  label: "General Health" },
  weight_loss: { calories: 1600, protein: 120, carbs: 180, fats: 55, fiber: 38, sugar: 25,  label: "Weight Loss" },
  diabetes:    { calories: 2000, protein: 120, carbs: 195, fats: 70, fiber: 45, sugar: 25,  label: "Diabetes" },
  high_bp:     { calories: 2000, protein: 120, carbs: 300, fats: 55, fiber: 40, sugar: 36,  label: "High BP" },
};

const FOOD_SUGGESTIONS = [
  "rice","brown rice","roti","bread","oatmeal","poha","upma","dosa","idli","noodles","pasta",
  "egg","chicken","fish","dal","sambar","paneer","rajma","chickpeas",
  "milk","curd","butter","ghee","cheese",
  "apple","banana","orange","mango","grapes","watermelon","papaya","guava",
  "salad","spinach","broccoli","carrot","tomato","potato","sweet potato",
  "pizza","burger","french fries","samosa","biscuit","chocolate","ice cream",
  "coffee","tea","green tea","juice","soda","water",
  "ladoo","halwa","kheer"
];

let state = {
  condition: "general",
  daily: { calories:0, protein:0, carbs:0, fats:0, fiber:0, sugar:0 },
  entries: [],
  entryCount: 0
};

// ─────────────────────────────────────────────
// DOM References
// ─────────────────────────────────────────────
const $ = id => document.getElementById(id);

const els = {
  foodInput:         $("foodInput"),
  portionInput:      $("portionInput"),
  mealType:          $("mealType"),
  btnBefore:         $("btnBefore"),
  btnAfter:          $("btnAfter"),
  spinner:           $("spinner"),
  resultPanel:       $("resultPanel"),
  warningBanner:     $("warningBanner"),
  conditionGrid:     $("conditionGrid"),
  conditionBadge:    $("conditionBadgeText"),
  calNum:            $("calNum"),
  calTarget:         $("calTarget"),
  calEntries:        $("calEntries"),
  calCircle:         $("calCircle"),
  barProtein:        $("barProtein"),
  barCarbs:          $("barCarbs"),
  barFats:           $("barFats"),
  barFiber:          $("barFiber"),
  barSugar:          $("barSugar"),
  valProtein:        $("valProtein"),
  valCarbs:          $("valCarbs"),
  valFats:           $("valFats"),
  valFiber:          $("valFiber"),
  valSugar:          $("valSugar"),
  dailyScoreRow:     $("dailyScoreRow"),
  dailyScoreBadge:   $("dailyScoreBadge"),
  weekBars:          $("weekBars"),
  weekInsight:       $("weekInsight"),
  logCard:           $("logCard"),
  logList:           $("logList"),
  logCount:          $("logCount"),
  autocompleteList:  $("autocompleteList"),
  headerDate:        $("headerDate"),
  todayLabel:        $("todayLabel"),
};

// ─────────────────────────────────────────────
// Init
// ─────────────────────────────────────────────
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
  const opts = { weekday:"long", year:"numeric", month:"long", day:"numeric" };
  const label = now.toLocaleDateString("en-IN", opts);
  els.headerDate.textContent = label;
  if (els.todayLabel) els.todayLabel.textContent = now.toLocaleDateString("en-IN", { day:"2-digit", month:"short" });
}

// ─────────────────────────────────────────────
// Condition Panel
// ─────────────────────────────────────────────
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
  els.conditionBadge.textContent = target.label;
  els.conditionBadge.className = "badge badge-" + condBadgeColor(cond);
  els.calTarget.textContent = `Target: ${target.calories} kcal`;
  updateDailyBars(state.daily);
  localStorage.setItem("nutriguard_condition", cond);
}

function condBadgeColor(cond) {
  return { general:"green", weight_loss:"yellow", diabetes:"red", high_bp:"blue" }[cond] || "green";
}

function restoreCondition() {
  const saved = localStorage.getItem("nutriguard_condition") || "general";
  setCondition(saved);
}

// ─────────────────────────────────────────────
// Food Input & Autocomplete
// ─────────────────────────────────────────────
function initInputListeners() {
  els.btnBefore.addEventListener("click", () => submitFood("before"));
  els.btnAfter.addEventListener("click",  () => submitFood("after"));
  els.foodInput.addEventListener("input",  handleAutocomplete);
  els.foodInput.addEventListener("keydown", e => {
    if (e.key === "Enter") submitFood("after");
  });
  document.addEventListener("click", e => {
    if (!e.target.closest(".food-input-wrap")) closeAutocomplete();
  });
  $("btnClearToday").addEventListener("click", clearToday);
}

function handleAutocomplete() {
  const val = els.foodInput.value.toLowerCase().trim();
  if (val.length < 2) { closeAutocomplete(); return; }

  const matches = FOOD_SUGGESTIONS.filter(f => f.includes(val)).slice(0, 8);
  if (!matches.length) { closeAutocomplete(); return; }

  els.autocompleteList.innerHTML = matches.map(m =>
    `<div class="ac-item" data-val="${m}">${capitalize(m)}</div>`
  ).join("");
  els.autocompleteList.style.display = "block";

  els.autocompleteList.querySelectorAll(".ac-item").forEach(item => {
    item.addEventListener("click", () => {
      els.foodInput.value = item.dataset.val;
      closeAutocomplete();
    });
  });
}

function closeAutocomplete() {
  els.autocompleteList.style.display = "none";
  els.autocompleteList.innerHTML = "";
}

// ─────────────────────────────────────────────
// Submit Food
// ─────────────────────────────────────────────
async function submitFood(mode) {
  const food = els.foodInput.value.trim();
  if (!food) {
    showBanner("🍽 Please enter a food item first!", "yellow");
    return;
  }

  const portion  = parseFloat(els.portionInput.value) || 1.0;
  const mealType = els.mealType.value;
  const endpoint = mode === "before" ? "/api/analyze" : "/api/log";

  showSpinner(true);
  hideResult();

  try {
    const res = await fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        food, portion, meal_type: mealType, health_condition: state.condition
      })
    });
    const data = await res.json();

    if (!res.ok) {
      showBanner(data.error || "Something went wrong.", "red");
      return;
    }

    renderResult(data, mode);

    if (mode === "after") {
      state.daily = data.daily_totals || state.daily;
      state.entryCount = data.entries_today || 0;
      updateDailyPanel();
      loadDailySummary();        // refresh score
      loadWeeklySummary();       // refresh week bars
      refreshLogCard();          // refresh food log
    }

    els.foodInput.value = "";
    els.portionInput.value = "1";
    closeAutocomplete();

  } catch (err) {
    showBanner("Network error. Please try again.", "red");
  } finally {
    showSpinner(false);
  }
}

// ─────────────────────────────────────────────
// Render Result
// ─────────────────────────────────────────────
function renderResult(data, mode) {
  const rec = data.recommendation || {};
  const analysis = data.analysis || {};
  const nutrition = data.nutrition || {};
  const severity = rec.severity || "green";

  // Warning banner
  if (severity === "red") {
    showBanner("🚨 " + (rec.warnings?.[0] || rec.summary), "red");
  } else if (severity === "yellow") {
    showBanner("⚡ " + (rec.summary || "Moderate choice. Eat in balance."), "yellow");
  } else {
    hideBanner();
  }

  // Result card
  const card = document.querySelector(".result-card");
  card.className = `card result-card severity-${severity}`;

  $("resultFoodName").textContent = "🍽 " + capitalize(data.food || "");

  const modeBadge = $("resultModeBadge");
  modeBadge.textContent = mode === "before" ? "📋 Pre-Analysis" : "✅ Logged";
  modeBadge.className = "result-mode-badge " + (mode === "before" ? "mode-before" : "mode-after");

  // Health score
  const score = rec.health_score ?? 0;
  $("scoreNum").textContent = score.toFixed(1);
  $("scoreLabel").textContent = rec.score_label || "";
  $("scoreSummary").textContent = rec.summary || "";
  const scoreCircle = $("scoreCircle");
  scoreCircle.className = "score-circle " + (score >= 6 ? "score-green" : score >= 4 ? "score-yellow" : "score-red");

  // Nutrition chips
  $("nutritionChips").innerHTML = [
    { k:"calories", label:"Calories", unit:"kcal", cls:"chip-cal" },
    { k:"protein",  label:"Protein",  unit:"g",    cls:"chip-protein" },
    { k:"carbs",    label:"Carbs",    unit:"g",    cls:"chip-carbs" },
    { k:"fats",     label:"Fats",     unit:"g",    cls:"chip-fats" },
    { k:"fiber",    label:"Fiber",    unit:"g",    cls:"chip-fiber" },
    { k:"sugar",    label:"Sugar",    unit:"g",    cls:"chip-sugar" },
  ].map(({ k, label, unit, cls }) =>
    `<div class="chip ${cls}">
       <span class="chip-val">${nutrition[k] ?? 0}${unit}</span>
       <span class="chip-label">${label}</span>
     </div>`
  ).join("");

  renderList("resultWarnings",     "warningList",     rec.warnings || [],     true);
  renderList("resultPositives",    "positiveList",    rec.positives || [],    true);
  renderList("resultSuggestions",  "suggestionList",  rec.suggestions || [],  true);
  renderList("resultAlternatives", "alternativeList", rec.alternatives || [], true);
  renderList("resultTips",         "tipList",         rec.tips || [],         true);

  els.resultPanel.style.display = "block";
  els.resultPanel.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

function renderList(wrapperId, listId, items, show) {
  const wrapper = $(wrapperId);
  const list    = $(listId);
  if (!items || !items.length) { wrapper.style.display = "none"; return; }
  list.innerHTML = items.map(i => `<li>${i}</li>`).join("");
  wrapper.style.display = "block";
}

// ─────────────────────────────────────────────
// Daily Panel Updates
// ─────────────────────────────────────────────
function updateDailyPanel() {
  const d = state.daily;
  const targets = CONDITION_TARGETS[state.condition] || CONDITION_TARGETS.general;

  els.calNum.textContent = Math.round(d.calories || 0);
  els.calEntries.textContent = `${state.entryCount} item${state.entryCount !== 1 ? "s" : ""} logged`;

  const calOver = (d.calories || 0) > targets.calories;
  els.calCircle.className = "cal-circle" + (calOver ? " over" : "");

  updateBar("barProtein", "valProtein", d.protein,  targets.protein,  "g");
  updateBar("barCarbs",   "valCarbs",   d.carbs,    targets.carbs,    "g");
  updateBar("barFats",    "valFats",    d.fats,     targets.fats,     "g");
  updateBar("barFiber",   "valFiber",   d.fiber,    targets.fiber,    "g");
  updateBar("barSugar",   "valSugar",   d.sugar,    targets.sugar,    "g");
}

function updateBar(barId, valId, value, max, unit) {
  const pct = Math.min((value / max) * 100, 100);
  const el  = $(barId);
  const over = value > max;
  el.style.width = pct + "%";
  el.classList.toggle("over", over);
  $(valId).textContent = (value || 0).toFixed(1) + unit;
}

function updateDailyBars(totals) {
  // Re-render bars when condition changes
  if (!totals) return;
  const targets = CONDITION_TARGETS[state.condition] || CONDITION_TARGETS.general;
  updateBar("barProtein", "valProtein", totals.protein || 0,  targets.protein, "g");
  updateBar("barCarbs",   "valCarbs",   totals.carbs  || 0,  targets.carbs,   "g");
  updateBar("barFats",    "valFats",    totals.fats   || 0,  targets.fats,    "g");
  updateBar("barFiber",   "valFiber",   totals.fiber  || 0,  targets.fiber,   "g");
  updateBar("barSugar",   "valSugar",   totals.sugar  || 0,  targets.sugar,   "g");
  els.calTarget.textContent = `Target: ${targets.calories} kcal`;
}

// ─────────────────────────────────────────────
// Load Daily Summary from API
// ─────────────────────────────────────────────
async function loadDailySummary() {
  try {
    const res  = await fetch("/api/daily_summary");
    const data = await res.json();

    state.daily      = data.totals || {};
    state.entryCount = data.entry_count || 0;
    state.entries    = data.entries || [];

    els.calNum.textContent = Math.round(state.daily.calories || 0);
    els.calEntries.textContent = `${state.entryCount} item${state.entryCount !== 1 ? "s" : ""} logged`;

    updateDailyBars(state.daily);

    // Daily health score
    if (data.health_score !== null && data.health_score !== undefined) {
      els.dailyScoreRow.style.display = "flex";
      els.dailyScoreBadge.textContent = data.health_score.toFixed(1) + " / 10";
      els.dailyScoreBadge.style.color = scoreColor(data.health_score);
    }

    refreshLogCard();
  } catch (e) {
    console.warn("Could not load daily summary", e);
  }
}

function scoreColor(score) {
  if (score >= 7) return "#2e7d32";
  if (score >= 4) return "#e65100";
  return "#b71c1c";
}

// ─────────────────────────────────────────────
// Food Log Card
// ─────────────────────────────────────────────
function refreshLogCard() {
  if (!state.entries || !state.entries.length) {
    els.logCard.style.display = "none";
    return;
  }
  els.logCard.style.display = "block";
  els.logCount.textContent = state.entries.length + " items";
  els.logList.innerHTML = state.entries.map(entry => {
    const cat = entry.nutrition?.category || "other";
    return `
      <div class="log-item cat-${cat}">
        <div class="log-item-left">
          <span class="log-food-name">${capitalize(entry.food)} × ${entry.portion}</span>
          <span class="log-meta">${entry.meal_type} · ${entry.time}</span>
        </div>
        <span class="log-cal">${Math.round(entry.nutrition?.calories || 0)} kcal</span>
      </div>`;
  }).join("");
}

// ─────────────────────────────────────────────
// Weekly Summary
// ─────────────────────────────────────────────
async function loadWeeklySummary() {
  try {
    const res  = await fetch("/api/weekly_summary");
    const data = await res.json();
    renderWeekBars(data.weekly || []);
  } catch (e) {
    console.warn("Could not load weekly summary", e);
  }
}

function renderWeekBars(days) {
  if (!days.length) return;

  const maxCal = Math.max(...days.map(d => d.totals?.calories || 0), 500);
  const todayStr = new Date().toISOString().split("T")[0];

  els.weekBars.innerHTML = days.map(d => {
    const cal   = d.totals?.calories || 0;
    const pct   = Math.max((cal / maxCal) * 60, cal > 0 ? 4 : 0);
    const isToday = d.date === todayStr;
    const isEmpty = cal === 0;
    return `
      <div class="week-bar-col" title="${d.day}: ${Math.round(cal)} kcal">
        <div class="week-bar ${isEmpty ? "empty" : ""} ${isToday ? "today" : ""}"
             style="height:${pct}px"></div>
        <span class="week-day-label">${d.day}</span>
      </div>`;
  }).join("");

  // Insight
  const activeDays = days.filter(d => (d.totals?.calories || 0) > 0);
  if (activeDays.length > 0) {
    const avgCal = activeDays.reduce((s, d) => s + (d.totals?.calories || 0), 0) / activeDays.length;
    els.weekInsight.textContent = `${activeDays.length}/7 days tracked · Avg ${Math.round(avgCal)} kcal/day`;
    els.weekInsight.style.display = "block";
  }
}

// ─────────────────────────────────────────────
// Clear Today
// ─────────────────────────────────────────────
async function clearToday() {
  if (!confirm("Clear all of today's food log?")) return;
  await fetch("/api/clear_today", { method: "POST" });
  state.daily = { calories:0, protein:0, carbs:0, fats:0, fiber:0, sugar:0 };
  state.entryCount = 0;
  state.entries = [];
  els.calNum.textContent = "0";
  els.calEntries.textContent = "0 items logged";
  ["barProtein","barCarbs","barFats","barFiber","barSugar"].forEach(id => $(id).style.width = "0%");
  ["valProtein","valCarbs","valFats","valFiber","valSugar"].forEach(id => $(id).textContent = "0g");
  els.dailyScoreRow.style.display = "none";
  els.logCard.style.display = "none";
  hideResult();
  hideBanner();
  loadWeeklySummary();
}

// ─────────────────────────────────────────────
// Helpers
// ─────────────────────────────────────────────
function showSpinner(on) { els.spinner.style.display = on ? "flex" : "none"; }
function hideResult()    { els.resultPanel.style.display = "none"; }

function showBanner(msg, type) {
  els.warningBanner.innerHTML = `<span>${msg}</span>`;
  els.warningBanner.style.display = "flex";
  els.warningBanner.style.background =
    type === "red"    ? "linear-gradient(135deg, #e53935, #b71c1c)" :
    type === "yellow" ? "linear-gradient(135deg, #f9a825, #e65100)" :
                        "linear-gradient(135deg, #2e7d32, #388e3c)";
}

function hideBanner() { els.warningBanner.style.display = "none"; }

function capitalize(str) {
  return str ? str.charAt(0).toUpperCase() + str.slice(1) : "";
}
