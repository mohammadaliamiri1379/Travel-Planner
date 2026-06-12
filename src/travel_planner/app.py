from datetime import datetime

import streamlit as st
import httpx
import pandas as pd
import pydeck as pdk
from travel_planner.UI.ui_styles import apply_custom_css
from travel_planner.UI.reels_demo import render_destination_reels
from travel_planner.Utils.utils import generate_follow_up_questions, generate_final_plan

STEP_ANCHORS = {
    "input": "step-anchor-input",
    "questions": "step-anchor-questions",
    "results": "step-anchor-results",
}


def _scroll_to_anchor_js(anchor_id: str) -> str:
    # scrollIntoView walks up the real scroll container (whatever it is) and
    # scrolls in whichever direction is needed, unlike a hardcoded
    # scrollTo(0) on a guessed container. Streamlit's main container also
    # auto-scrolls to follow new content as it streams in, which can fight a
    # one-shot scroll - keep re-asserting for a bit so ours wins.
    return f"""
<script>
    (function () {{
        const tryScroll = () => {{
            const el = document.getElementById("{anchor_id}");
            if (el) {{
                el.scrollIntoView({{behavior: "smooth", block: "start"}});
            }}
        }};
        let ticks = 0;
        const interval = setInterval(() => {{
            tryScroll();
            ticks += 1;
            if (ticks > 15) clearInterval(interval);
        }}, 100);
        tryScroll();
    }})();
</script>
"""

DEFAULT_GATEWAY_BASE_URL = "http://127.0.0.1:8000"


def _format_trip_dates(start_iso: str, end_iso: str) -> str:
    """Format a trip's start/end dates (ISO strings) as e.g. "June 15-17, 2026"."""
    start = datetime.fromisoformat(start_iso).date()
    end = datetime.fromisoformat(end_iso).date()

    if start == end:
        return start.strftime("%B %d, %Y")
    if (start.year, start.month) == (end.year, end.month):
        return f"{start.strftime('%B %d')}-{end.day}, {end.year}"
    if start.year == end.year:
        return f"{start.strftime('%B %d')} - {end.strftime('%B %d, %Y')}"
    return f"{start.strftime('%B %d, %Y')} - {end.strftime('%B %d, %Y')}"

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


def _maybe_auto_submit(num_questions: int) -> None:
    """Once every question has an answer, treat Enter on the last field as submit."""
    if all(st.session_state.get(f"answer_{i}", "").strip() for i in range(num_questions)):
        st.session_state._auto_submit = True


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

if "_last_rendered_step" not in st.session_state:
    st.session_state._last_rendered_step = st.session_state.step

if "destination_city" not in st.session_state:
    st.session_state.destination_city = ""

if "weather" not in st.session_state:
    st.session_state.weather = []

# ----------------------------
# HEADER
# ----------------------------
st.markdown('<div class="title">🌍 AI Travel Planner</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Tell me your dream trip, I’ll build your itinerary</div>', unsafe_allow_html=True)

# ----------------------------
# STEP 1: INPUT
# ----------------------------
if st.session_state.step == "input":

    st.markdown('<div id="step-anchor-input"></div>', unsafe_allow_html=True)
    st.markdown("### ✈️ Where do you want to go?")

    st.caption("Tip: press **Ctrl + Enter** in the box below to submit.")

    with st.form("trip_form", border=False):
        prompt = st.text_area(
            "",
            placeholder="e.g. I want a 3-day romantic trip to Paris with museums and food",
            height=120,
            key="prompt_input"
        )
        submitted = st.form_submit_button("✨ Create my itinerary", type="primary", use_container_width=True)

    if submitted:
        st.session_state.user_prompt = prompt

        with st.spinner("✨ Thinking about your trip..."):
            st.session_state.questions = generate_follow_up_questions(DEFAULT_GATEWAY_BASE_URL, prompt)

        if st.session_state.questions and len(st.session_state.questions) > 0:
            st.session_state.step = "questions"
        else:
            with st.spinner("🧭 Crafting your itinerary..."):
                plan = generate_final_plan(DEFAULT_GATEWAY_BASE_URL, prompt, {})
            st.session_state.results = plan["itinerary"]
            st.session_state.destination_city = plan["where"]
            st.session_state.weather = plan["weather"]
            st.session_state.step = "results"

# ----------------------------
# STEP 2: QUESTIONS
# ----------------------------
if st.session_state.step == "questions":

    st.markdown('<div id="step-anchor-questions"></div>', unsafe_allow_html=True)
    st.markdown("### 🤔 A few quick questions")
    st.caption("Tip: press **Enter** after answering the last question to continue.")

    num_questions = len(st.session_state.questions)
    for i, q in enumerate(st.session_state.questions):
        with st.container(border=True):
            answer_key = f"answer_{i}"
            st.session_state.answers[q] = st.text_input(
                q,
                key=answer_key,
                on_change=_maybe_auto_submit,
                args=(num_questions,),
            )

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

    generate_clicked = st.button("🚀 Generate plan", type="primary", use_container_width=True)
    auto_submit = st.session_state.pop("_auto_submit", False)

    if generate_clicked or auto_submit:
        with st.spinner("🧭 Crafting your itinerary..."):
            plan = generate_final_plan(
                DEFAULT_GATEWAY_BASE_URL,
                st.session_state.user_prompt,
                st.session_state.answers
            )
        st.session_state.results = plan["itinerary"]
        st.session_state.destination_city = plan["where"]
        st.session_state.weather = plan["weather"]
        st.session_state.step = "results"

# ----------------------------
# STEP 3: RESULTS
# ----------------------------
if st.session_state.step == "results":

    st.markdown('<div id="step-anchor-results"></div>', unsafe_allow_html=True)
    st.markdown("### 🧭 Your Travel Itinerary")

    render_destination_reels(st.session_state.destination_city)

    results = st.session_state.results

    days: dict[int, list[dict]] = {}
    for place in results:
        days.setdefault(place.get("day", 1), []).append(place)

    # Number every stop in the same order it will be displayed below, so the
    # map pins and the itinerary cards share the same "1, 2, 3..." labels.
    ordered_places = [place for day in sorted(days) for place in days[day]]
    for number, place in enumerate(ordered_places, start=1):
        place["_marker_number"] = number

    map_points = [
        {
            "lat": place["lat"],
            "lon": place["lon"],
            "label": str(place["_marker_number"]),
            "title": place.get("title", ""),
            "time": place.get("time", ""),
            "day": place.get("day", 1),
        }
        for place in ordered_places
        if place.get("lat") is not None and place.get("lon") is not None
    ]
    if map_points:
        st.markdown("#### 🗺️ Map of your stops")
        df = pd.DataFrame(map_points)

        paths_by_day: dict[int, list[list[float]]] = {}
        for point in map_points:
            paths_by_day.setdefault(point["day"], []).append([point["lon"], point["lat"]])
        route_df = pd.DataFrame({"path": [coords for coords in paths_by_day.values() if len(coords) > 1]})

        view_state = pdk.ViewState(
            latitude=df["lat"].mean(),
            longitude=df["lon"].mean(),
            zoom=12,
            pitch=35,
        )
        route_layer = pdk.Layer(
            "PathLayer",
            data=route_df,
            get_path="path",
            get_color=[56, 189, 248, 140],
            get_width=3,
            width_min_pixels=2,
            rounded=True,
            pickable=False,
        )
        pin_layer = pdk.Layer(
            "ScatterplotLayer",
            data=df,
            get_position="[lon, lat]",
            get_fill_color=[56, 189, 248, 230],
            get_line_color=[15, 23, 42, 255],
            line_width_min_pixels=2,
            get_radius=1,
            radius_units="pixels",
            radius_min_pixels=16,
            radius_max_pixels=16,
            stroked=True,
            pickable=True,
        )
        label_layer = pdk.Layer(
            "TextLayer",
            data=df,
            get_position="[lon, lat]",
            get_text="label",
            get_size=14,
            get_color=[255, 255, 255, 255],
            get_text_anchor="'middle'",
            get_alignment_baseline="'center'",
        )
        st.pydeck_chart(pdk.Deck(
            layers=[route_layer, pin_layer, label_layer],
            initial_view_state=view_state,
            map_provider="carto",
            map_style=pdk.map_styles.DARK,
            tooltip={
                "html": "<b>Stop {label}: {title}</b><br/>🕒 {time}",
                "style": {"backgroundColor": "#1e293b", "color": "#e2e8f0", "fontSize": "13px"},
            },
        ))

    weather_by_day = {w["day"]: w for w in st.session_state.weather}

    first_iso = ordered_places[0].get("date_iso") if ordered_places else ""
    last_iso = ordered_places[-1].get("date_iso") if ordered_places else ""
    if st.session_state.destination_city:
        title = f"### 🌍 {st.session_state.destination_city} Trip"
        if first_iso and last_iso:
            title += f", {_format_trip_dates(first_iso, last_iso)}"
        st.markdown(title)

    for day in sorted(days):
        day_places = days[day]
        date_iso = day_places[0].get("date_iso")
        date_label = datetime.fromisoformat(date_iso).strftime("%A, %B %d") if date_iso else day_places[0].get("date")
        header = f"#### 📅 Day {day}" + (f" - {date_label}" if date_label else "")

        day_weather = weather_by_day.get(day)
        if day_weather:
            condition = day_weather.get("condition", "")
            high = day_weather.get("temp_high_c")
            low = day_weather.get("temp_low_c")
            precip = day_weather.get("precipitation_chance")
            temp_str = f" {high:.0f}°/{low:.0f}°C" if high is not None and low is not None else ""
            precip_str = f" · 💧{precip}%" if precip is not None else ""
            header += f"&nbsp;&nbsp;{condition}{temp_str}{precip_str}"

        st.markdown(header)

        for place in day_places:
            time_label = place.get("time", "")
            time_prefix = f"🕒 {time_label} &nbsp;·&nbsp; " if time_label else ""
            delay = min((place["_marker_number"] - 1) * 0.05, 0.6)
            st.markdown(f"""
            <div class="card" style="animation-delay: {delay:.2f}s;">
                <div class="place-title"><span class="marker-badge">{place['_marker_number']}</span>{time_prefix}📍 {place['title']}</div>
                <div class="address">📌 {place['address']}</div>
                <div class="desc">{place['description']}</div>
            </div>
            """, unsafe_allow_html=True)

    if st.button("🔁 Plan another trip", type="primary", use_container_width=True):
        st.session_state.clear()
        st.session_state.step = "input"
        st.session_state.prompt_input = ""
        st.session_state._last_rendered_step = "results"
        st.rerun()

# ----------------------------
# AUTO-SCROLL ON NEW CONTENT
# ----------------------------
if st.session_state.step != st.session_state._last_rendered_step:
    st.session_state._last_rendered_step = st.session_state.step
    anchor_id = STEP_ANCHORS.get(st.session_state.step, "step-anchor-input")
    st.html(_scroll_to_anchor_js(anchor_id), unsafe_allow_javascript=True)

# ----------------------------
# FOOTER
# ----------------------------
st.markdown(
    '<div class="footer">© 2026 Christopher Khoury &amp; Mohamadali Amiri. All rights reserved.</div>',
    unsafe_allow_html=True,
)