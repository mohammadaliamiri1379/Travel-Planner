import streamlit as st
import httpx
import pandas as pd
from travel_planner.UI.ui_styles import apply_custom_css
from travel_planner.Utils.utils import Call_Orchestrator, generate_follow_up_questions, generate_final_plan

DEFAULT_GATEWAY_BASE_URL = "http://127.0.0.1:8000"

DATE_SUGGESTIONS = ["Next week", "Next month", "In 2 months", "This summer"]
DURATION_SUGGESTIONS = ["2 days", "3 days", "5 days", "7 days"]
INTEREST_SUGGESTIONS = ["Food & coffee", "Museums & art", "History & culture", "Nature & parks", "Nightlife", "Shopping", "Gelato & dessert"]

SUGGESTIONS_PER_ROW = 4


def suggestions_for_question(question: str) -> tuple[list[str], bool]:
    """Pick a row of popular quick-reply suggestions based on the question's topic.

    Returns (suggestions, multi_select) - interests support picking several at once,
    everything else is a single choice.
    """
    q = question.lower()
    # Destination questions (e.g. "what cities are you interested in visiting?")
    # don't have a meaningful generic suggestion - skip those first.
    if any(keyword in q for keyword in ["city", "cities", "destination", "where"]):
        return [], False
    if any(keyword in q for keyword in ["how many days", "duration", "how long", "length of"]):
        return DURATION_SUGGESTIONS, False
    if any(keyword in q for keyword in ["when", "date", "month", "time of year"]):
        return DATE_SUGGESTIONS, False
    if any(keyword in q for keyword in ["interest", "like to do", "prefer", "enjoy", "activities", "activity"]):
        return INTEREST_SUGGESTIONS, True
    return [], False


def _apply_suggestion(answer_key: str, suggestion: str) -> None:
    st.session_state[answer_key] = suggestion


def _toggle_interest(answer_key: str, selected_key: str, suggestion: str, ordered_options: list[str]) -> None:
    selected: set[str] = st.session_state.setdefault(selected_key, set())
    if suggestion in selected:
        selected.discard(suggestion)
    else:
        selected.add(suggestion)
    st.session_state[answer_key] = ", ".join(option for option in ordered_options if option in selected)


st.set_page_config(
    page_title="AI Travel Planner",
    page_icon="🌍",
    layout="centered"
)

# ----------------------------
# CUSTOM CSS (makes it pretty)
# ----------------------------
apply_custom_css()

# ----------------------------
# SESSION STATE
# ----------------------------
if "step" not in st.session_state:
    st.session_state.step = "input"

if "user_prompt" not in st.session_state:
    st.session_state.user_prompt = ""

if "questions" not in st.session_state:
    st.session_state.questions = []

if "answers" not in st.session_state:
    st.session_state.answers = {}

if "results" not in st.session_state:
    st.session_state.results = []

if "prompt_input" not in st.session_state:
    st.session_state.prompt_input = ""

# ----------------------------
# HEADER
# ----------------------------
st.markdown('<div class="title">🌍 AI Travel Planner</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Tell me your dream trip — I’ll build your itinerary</div>', unsafe_allow_html=True)

# ----------------------------
# STEP 1: INPUT
# ----------------------------
if st.session_state.step == "input":

    st.markdown("### ✈️ Where do you want to go?")

    prompt = st.text_area(
        "",
        placeholder="e.g. I want a 3-day romantic trip to Paris with museums and food",
        height=120,
        key="prompt_input"
    )

    if st.button("✨ Create my itinerary", type="primary", use_container_width=True):
        st.session_state.user_prompt = prompt
        st.markdown("Generating your personalized itinerary... This may take a moment. ⏳")
        # msg = Call_Orchestrator(DEFAULT_GATEWAY_BASE_URL, prompt)
        # if "step" not in msg:
        #     raise KeyError("Missing 'step' in response")
        # st.session_state.step = msg["step"]

        st.session_state.questions = generate_follow_up_questions(DEFAULT_GATEWAY_BASE_URL, prompt)

        print( "len of questions: ", len(st.session_state.questions) )
        if st.session_state.questions and len(st.session_state.questions) > 0:
            st.session_state.step = "questions"
        else:
            st.session_state.results = generate_final_plan(DEFAULT_GATEWAY_BASE_URL, prompt, {})
            st.session_state.step = "results"

# ----------------------------
# STEP 2: QUESTIONS
# ----------------------------
if st.session_state.step == "questions":

    st.markdown("### 🤔 A few quick questions")

    for i, q in enumerate(st.session_state.questions):
        with st.container(border=True):
            answer_key = f"answer_{i}"
            st.session_state.answers[q] = st.text_input(q, key=answer_key)

            suggestions, multi = suggestions_for_question(q)
            if not suggestions:
                continue

            selected_key = f"selected_{i}"
            selected: set[str] = st.session_state.setdefault(selected_key, set())

            for row_start in range(0, len(suggestions), SUGGESTIONS_PER_ROW):
                row = suggestions[row_start:row_start + SUGGESTIONS_PER_ROW]
                cols = st.columns(len(row))
                for col, suggestion in zip(cols, row):
                    if multi:
                        is_selected = suggestion in selected
                        label = f"✅ {suggestion}" if is_selected else suggestion
                        col.button(
                            label,
                            key=f"suggestion_{i}_{suggestion}",
                            on_click=_toggle_interest,
                            args=(answer_key, selected_key, suggestion, suggestions),
                            use_container_width=True,
                        )
                    else:
                        is_selected = st.session_state.get(answer_key) == suggestion
                        label = f"✅ {suggestion}" if is_selected else suggestion
                        col.button(
                            label,
                            key=f"suggestion_{i}_{suggestion}",
                            on_click=_apply_suggestion,
                            args=(answer_key, suggestion),
                            use_container_width=True,
                        )

    if st.button("🚀 Generate plan", type="primary", use_container_width=True):
        st.session_state.results = generate_final_plan(
            DEFAULT_GATEWAY_BASE_URL,
            st.session_state.user_prompt,
            st.session_state.answers
        )
        st.session_state.step = "results"

# ----------------------------
# STEP 3: RESULTS
# ----------------------------
if st.session_state.step == "results":

    st.markdown("### 🧭 Your Travel Itinerary")

    results = st.session_state.results

    map_points = [
        {"lat": place["lat"], "lon": place["lon"]}
        for place in results
        if place.get("lat") is not None and place.get("lon") is not None
    ]
    if map_points:
        st.markdown("#### 🗺️ Map of your stops")
        st.map(pd.DataFrame(map_points))

    days: dict[int, list[dict]] = {}
    for place in results:
        days.setdefault(place.get("day", 1), []).append(place)

    for day in sorted(days):
        day_places = days[day]
        date_label = day_places[0].get("date") or f"Day {day}"
        st.markdown(f"#### 📅 Day {day} — {date_label}")

        for place in day_places:
            time_label = place.get("time", "")
            time_prefix = f"🕒 {time_label} &nbsp;·&nbsp; " if time_label else ""
            st.markdown(f"""
            <div class="card">
                <div class="place-title">{time_prefix}📍 {place['title']}</div>
                <div class="address">📌 {place['address']}</div>
                <div class="desc">{place['description']}</div>
            </div>
            """, unsafe_allow_html=True)

    if st.button("🔁 Plan another trip", type="primary", use_container_width=True):
        st.session_state.clear()
        st.session_state.step = "input"
        st.session_state.prompt_input = ""
        st.rerun()