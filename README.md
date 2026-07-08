# Raah Shumar (راہ شمار)

> Raah means route. Shumar means count.

An AI agent that autonomously allocates university buses based on real student demand — replacing the daily manual process of counting WhatsApp messages to decide how many buses to send.

Built at the **Agentic AI Hackathon 2026 · FAST NUCES Islamabad** by Team Null Pointers.

---

## The Problem

Every morning, a university transport coordinator manually counts WhatsApp messages to figure out how many buses to send, which routes need more capacity, and what size vehicles to deploy. It's repetitive, error-prone, and entirely manual.

Raah Shumar automates that entire decision.

---

## What It Does

**1. Student Poll**
Students submit an anonymous poll — no login, no personal data required. They select:
- Route (Wah Cantt, G Sector, H Sector, I Sector)
- Stop (within their route)
- Direction (Arrival or Departure)
- University (FAST NUCES, NUST, AIR University, Bahria University)
- Fleet (filtered by direction, shows their exact pickup time at their stop)

The poll closes 30 minutes before each fleet departs.

**2. AI Allocation Agent**
Once the poll closes, the agent runs once. It reads all submissions, groups them by route and fleet, and decides which vehicles to deploy:

| Students | Vehicle Decision |
|----------|-----------------|
| ≤ 5 | 1 Taxi |
| 6 – 15 | 1 Mini (15 seats) |
| 16 – 24 | 1 Coaster (24 seats) |
| 25 – 40 | 1 Bus (40 seats) |
| 41 – 55 | 1 Bus + 1 Mini |
| 56 – 64 | 1 Bus + 1 Coaster |
| 65 – 80 | 2 Buses |
| 80+ | Agent optimises combination |

Multiple vehicles on the same route travel as a convoy. The agent explains every decision out loud — not just an output, but a reasoned allocation you can read and verify.

**3. Dashboard — Two Views**
- **Transport Office View** — full schedule, all routes, all fleets, agent reasoning per decision
- **Student View (Check My Bus)** — student selects route, stop, direction, and fleet to see their assigned vehicle and exact pickup time

---

## The Agentic Loop

```
Poll Collects → Data Stores → Agent Decides → Dashboard Publishes
```

Poll closes → Agent runs once → Schedule is locked.

No per-submission re-runs. Bus allocation is a collective decision — the agent needs all the data before deciding anything.

---

## Why One Agent

Every other team at the hackathon had multi-agent pipelines. Ours had one.

A data collection agent would just be a CSV writer. A display agent would just be a Streamlit renderer. Neither involves reasoning. Our single agent observes poll data, reasons through demand, optimises vehicle combinations, and returns explainable decisions. That is a complete agentic loop.

Not everything needs AI. And adding more of it doesn't necessarily mean more quality.

---

## Tech Stack

| Layer | Tool |
|-------|------|
| LLM | Gemini 1.5 Flash |
| Frontend + Backend | Streamlit |
| Language | Python |
| Storage | CSV (polls.csv, allocations.csv) |
| Deployment | Streamlit Community Cloud |

---

## Project Structure

```
transport_portal/
├── app.py
├── requirements.txt
├── .env
├── data/
│   ├── polls.csv
│   └── allocations.csv
└── src/
    ├── data/
    │   ├── __init__.py
    │   └── store.py
    ├── agent/
    │   ├── __init__.py
    │   └── allocator.py
    └── ui/
        ├── __init__.py
        ├── poll_form.py
        ├── dashboard.py
        └── student_view.py
```

---

## Routes & Fleet Data

**Routes**
| Route | Stops |
|-------|-------|
| Route A — Wah Cantt | Wah Cantt 1, 2, 3, 4 |
| Route B — G Sector | G-9, G-10, G-11, G-13 |
| Route C — H Sector | H-8, H-9, H-11, H-13 |
| Route D — I Sector | I-8, I-9, I-10, I-11 |

All routes serve: FAST NUCES, NUST, AIR University, Bahria University.

**Fleet Schedule**
| Fleet | Direction | Base Time |
|-------|-----------|-----------|
| Fleet 1 | Arrival | 7:00 AM |
| Fleet 2 | Arrival | 8:00 AM |
| Fleet 3 | Arrival | 9:00 AM |
| Fleet 4 | Departure | 12:00 PM |
| Fleet 5 | Departure | 2:00 PM |
| Fleet 6 | Arrival | 4:00 PM |
| Fleet 7 | Departure | 6:00 PM |
| Fleet 8 | Departure | 8:00 PM |

Timing logic: each stop adds +10 minutes from the fleet base time based on stop index. Universities follow the order: Bahria → FAST → AIR → NUST for departure fleets, reversed for arrivals.

**Vehicle Fleet**
| Type | Capacity |
|------|----------|
| Bus | 40 seats |
| Coaster | 24 seats |
| Mini | 15 seats |
| Taxi | 4 seats (edge case) |

---

## Local Setup

**1. Clone the repo**
```bash
git clone https://github.com/yourusername/raah-shumar.git
cd raah-shumar
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Add your Gemini API key**
Create a `.env` file in the root:
```
GEMINI_API_KEY=your_key_here
```

**4. Run the app**
```bash
streamlit run app.py
```

---

## Deployment

Deployed on Streamlit Community Cloud.

**To deploy your own instance:**
1. Push the repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repo, set `app.py` as the main file
4. Add `GEMINI_API_KEY` in the secrets manager
5. Deploy

---

## Team Null Pointers

| Member | Role |
|--------|------|
| Saliha Adan | AI allocation agent, data layer, deployment |
| Anum Ibrahim | Student poll, app flow, sample data |
| Umna Chaudhry | Idea, dashboard UI, student view |

---

## Demo

🎬 Loom demo: [link]
