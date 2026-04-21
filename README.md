# 🥗 My Food – Food & Health Smart Assistant

**Vertical:** Food & Health  
**Built with:** AI Agents in Google Antigravity IDE  
**Deployed on:** Google Cloud Run  

---

## 📌 Problem Statement

Millions of people make poor daily food choices due to lack of instant, personalised nutritional feedback. Most nutrition apps are either too complex, require internet/API access, or don't adapt to individual health conditions. People managing diabetes, high blood pressure, or weight need specific, contextual guidance — not generic advice.

---

## 💡 Solution Approach

My Food is a lightweight, agent-based smart assistant that:
- Accepts natural food input ("2 bowls of rice", "1 banana")
- Analyses nutritional content using a compact built-in database
- Adapts all recommendations to the user's selected health condition
- Tracks daily macro/micro-nutrient intake with visual progress bars
- Gives an instant health score and actionable suggestions — no external APIs needed

---

## 🤖 Agent-Based Architecture

The backend is structured as a pipeline of 5 logical agents:

```
User Input
    │
    ▼
┌─────────────────────────────┐
│  1. Input Agent             │  Parses food name, portion, aliases
│     input_agent.py          │
└────────────┬────────────────┘
             │
             ▼
┌─────────────────────────────┐
│  2. Nutrition Agent         │  Looks up nutrition DB (60+ foods)
│     nutrition_agent.py      │  Returns calories, protein, carbs, fats, fiber, sugar
└────────────┬────────────────┘
             │
             ▼
┌─────────────────────────────┐
│  3. Analysis Agent          │  Evaluates food vs daily targets
│     analysis_agent.py       │  Checks condition-specific limits
│                             │  Returns severity: green / yellow / red
└────────────┬────────────────┘
             │
             ▼
┌─────────────────────────────┐
│  4. Recommendation Agent    │  Generates warnings, suggestions, alternatives
│     recommendation_agent.py │  Computes health score (0–10)
└────────────┬────────────────┘
             │
             ▼
┌─────────────────────────────┐
│  5. Tracking Agent          │  Updates daily log, computes weekly stats
│     tracking_agent.py       │  Tracks streaks and progress insights
└─────────────────────────────┘
```

---

## 🧠 Core Features

| Feature | Description |
|---|---|
| Food Input System | Two modes: "I will eat this" (pre-analysis) and "I have eaten this" (log) |
| Daily Health Monitor | Tracks calories, protein, carbs, fats, fiber, sugar with progress bars |
| Health Condition Panel | Adapts targets for General, Weight Loss, Diabetes, High BP |
| Smart Recommendations | Warnings, suggestions, alternatives, and health score per food item |
| Weekly Tracking | 7-day visual chart and daily average insights |

---

## 🎨 UI Highlights

- **Font:** Poppins (all sizes)
- **Colors:** Red + Yellow theme, white background
- **Layout:** Card-based, responsive 2-column grid
- **Indicators:** Green (healthy), Yellow (moderate), Red (warning)
- **UX:** Instant feedback, no page reloads, autocomplete input

---

## 📦 Project Structure

```
My_Food/
├── app.py                    # Flask app + API routes
├── requirements.txt          # Flask + Gunicorn only
├── Dockerfile                # Cloud Run deployment
├── .dockerignore
├── README.md
├── agents/
│   ├── __init__.py
│   ├── input_agent.py        # Agent 1: Input parsing
│   ├── nutrition_agent.py    # Agent 2: Nutrition lookup (60+ foods)
│   ├── analysis_agent.py     # Agent 3: Evaluation & scoring
│   ├── recommendation_agent.py # Agent 4: Advice generation
│   └── tracking_agent.py     # Agent 5: Daily/weekly tracking
├── templates/
│   └── index.html            # Full UI template
└── static/
    ├── style.css             # Theme & layout styles
    └── app.js                # Client-side logic
```

---

## 🚀 How to Run Locally

### Prerequisites
- Python 3.11+
- pip

### Steps

```bash
# 1. Navigate to project directory
cd My_Food

# 2. Create virtual environment (optional but recommended)
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
python app.py
```

Open your browser at: **http://localhost:8080**

---

## ☁️ Deploy to Google Cloud Run

### Prerequisites
- Google Cloud account
- `gcloud` CLI installed

### Step-by-Step

```bash
# Step 1: Authenticate
gcloud auth login

# Step 2: Set your project
gcloud config set project YOUR_PROJECT_ID

# Step 3: Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com

# Step 4: Navigate to project folder
cd My_Food

# Step 5: Build and deploy in one command
gcloud run deploy My Food \
  --source . \
  --region asia-south1 \
  --platform managed \
  --allow-unauthenticated \
  --port 8080 \
  --memory 256Mi \
  --timeout 60

# Step 6: Open the deployed URL shown in the output
```

> **Note:** Cloud Run will automatically build using your Dockerfile and serve on the given URL.

---

## 🧪 Example Test Cases

### Test 1: Healthy food (General Health)
- **Input:** "banana", I have eaten this
- **Expected:** Health score 8+/10, Green indicator, positive notes, low warning count

### Test 2: Junk food (Weight Loss mode)
- **Input:** "pizza", I will eat this
- **Expected:** Red warning banner, health score < 5, alternatives suggested (grilled chicken, salad)

### Test 3: High-sugar food (Diabetes mode)
- **Input:** "mango", I have eaten this
- **Expected:** Yellow/Red flag on sugar, tip about low-sugar fruits, suggestion to pair with protein

### Test 4: Excellent choice
- **Input:** "salad", I have eaten this
- **Expected:** Green indicator, score 9+/10, positive notes, no warnings

### Test 5: Over daily limit
- **Input:** Multiple high-calorie items logged → then "burger"
- **Expected:** Red daily calorie flag, strong warning, recovery suggestions

---

## ⚙️ API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Main app page |
| POST | `/api/analyze` | Pre-meal food analysis |
| POST | `/api/log` | Log food after eating |
| POST | `/api/set_condition` | Set health condition |
| GET | `/api/daily_summary` | Today's nutrition totals |
| GET | `/api/weekly_summary` | 7-day tracking data |
| POST | `/api/clear_today` | Reset today's log |
| GET | `/health` | Health check endpoint |

---

## ✅ Competition Compliance

| Requirement | Status |
|---|---|
| Built in Google Antigravity IDE | ✅ |
| Deployable on Google Cloud Run | ✅ |
| Repository size < 1 MB | ✅ |
| Single branch | ✅ |
| No external APIs | ✅ |
| Agent-based architecture (5 agents) | ✅ |
| Flask backend, PORT 8080 | ✅ |
| Poppins font, Red+Yellow theme | ✅ |
| No ML models or large datasets | ✅ |

---

*Made with ❤️ using AI Agents in Google Antigravity IDE*
