# AI Travel Planner

Describe your trip in plain English, answer a couple of quick follow-up
questions, and get a real, day-by-day itinerary — complete with places,
short descriptions, suggested times, and a numbered map.

## How it works

The app is three small services that talk to each other over HTTP:

| Service | Default port | File | Role |
|---|---|---|---|
| Streamlit UI | 8501 | `src/travel_planner/app.py` | Chat-style front end |
| Gateway | 8000 | `src/travel_planner/api/gateway.py` | API the UI talks to |
| Places Agent | 8001 | `src/travel_planner/Agents/PlacesAgent.py` | Finds real places via Geoapify |

Request flow:

1. The UI sends the user's prompt to the gateway's `/generate-questions`.
2. The gateway's orchestrator (Semantic Kernel + Groq) checks the prompt is
   travel-related, extracts what it can (destination, dates, duration,
   interests), and — if anything important is missing — returns follow-up
   questions.
3. The UI shows those questions with quick-reply suggestion chips
   (multi-select for interests).
4. Once answered, the UI calls `/generate-itinerary`. The gateway asks the
   Places Agent for points of interest near the destination that match the
   user's interests, schedules them across the trip's days and time slots,
   asks the LLM for a short description of each stop, and returns the
   itinerary.
5. The UI renders the itinerary as day-grouped cards plus a map where each
   pin is numbered to match the corresponding card.

## Setup

1. Python 3.10+
2. Install dependencies:

   ```powershell
   pip install -r Requirements.txt
   ```

3. Create a `.env` file in the project root with your API keys:

   ```
   GROQ_API_KEY=your_groq_key
   GEOAPIFY_API_KEY=your_geoapify_key
   ```

## Running it

Start each service in its own terminal from the project root (PowerShell):

```powershell
$env:PYTHONPATH = "src"
python -m uvicorn travel_planner.Agents.PlacesAgent:app --port 8001
```

```powershell
$env:PYTHONPATH = "src"
python -m uvicorn travel_planner.api.gateway:app --port 8000
```

```powershell
$env:PYTHONPATH = "src"
python -m streamlit run src/travel_planner/app.py
```

Then open http://localhost:8501.

## Features

- Natural-language trip prompts, e.g. *"I want a 3-day romantic trip to
  Paris with museums and food"*
- Follow-up questions with quick-reply chips (multi-select for interests,
  toggle on/off)
- Day-by-day itinerary with approximate dates and times
- Real points of interest from Geoapify, matched to the requested interests
- Short, AI-written description for each stop
- Numbered map of all stops, matching the numbers on the itinerary cards

## Project layout

- `src/travel_planner/Agents/Orchestrator.py` — planning pipeline
  (relevance → missing info → follow-up questions / trip details)
- `src/travel_planner/Agents/PlacesAgent.py` — Geoapify-backed
  recommendations, day/time scheduling, and place descriptions
- `src/travel_planner/mcp_tools/geoapify.py` — Geoapify API wrappers and
  interest → category mapping
- `src/travel_planner/registry/agent_registry.py` — maps agent name → base
  URL
- `src/travel_planner/models/` — Pydantic models shared across services
- `src/travel_planner/UI/` — Streamlit styling
- `prompts.yaml` — LLM prompt templates for each pipeline stage

## Author

Travel_planner was created in 2026 by Mohammadali Amiri. Built with
[Cookiecutter](https://github.com/cookiecutter/cookiecutter) and the
[audreyfeldroy/cookiecutter-pypackage](https://github.com/audreyfeldroy/cookiecutter-pypackage)
project template.
