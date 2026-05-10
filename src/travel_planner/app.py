import streamlit as st
import httpx
from travel_planner.UI.ui_styles import apply_custom_css
from travel_planner.Utils.utils import Call_Orchestrator, generate_follow_up_questions, generate_final_plan

DEFAULT_GATEWAY_BASE_URL = "http://127.0.0.1:8000"


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

    if st.button("✨ Create my itinerary"):
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
            st.session_state.results = generate_final_plan(prompt, {})
            st.session_state.step = "results"

# ----------------------------
# STEP 2: QUESTIONS
# ----------------------------
if st.session_state.step == "questions":

    st.markdown("### 🤔 A few quick questions")

    for i, q in enumerate(st.session_state.questions):
        st.session_state.answers[q] = st.text_input(q, key=i)

    if st.button("🚀 Generate plan"):
        st.session_state.results = generate_final_plan(
            st.session_state.user_prompt,
            st.session_state.answers
        )
        st.session_state.step = "results"

# ----------------------------
# STEP 3: RESULTS
# ----------------------------
if st.session_state.step == "results":

    st.markdown("### 🧭 Your Travel Itinerary")

    for place in st.session_state.results:

        st.markdown(f"""
        <div class="card">
            <div class="place-title">📍 {place['title']}</div>
            <div class="address">📌 {place['address']}</div>
            <div class="desc">{place['description']}</div>
        </div>
        """, unsafe_allow_html=True)

    if st.button("🔁 Plan another trip"):
        st.session_state.clear()
        st.session_state.step = "input"
        st.session_state.prompt_input = ""
        st.rerun()