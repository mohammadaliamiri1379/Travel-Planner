import streamlit as st

def apply_custom_css():
    st.markdown("""
    <style>
        .main {
            background-color: #0f172a;
            color: white;
        }

        .title {
            text-align: center;
            font-size: 44px;
            font-weight: 800;
            margin-bottom: 6px;
            background: linear-gradient(135deg, #38bdf8, #818cf8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .subtitle {
            text-align: center;
            color: #94a3b8;
            margin-bottom: 30px;
            font-size: 16px;
        }

        h4 {
            margin-top: 28px;
            padding-bottom: 6px;
            border-bottom: 1px solid #334155;
        }

        .card {
            background: #1e293b;
            padding: 20px;
            border-radius: 16px;
            margin-bottom: 15px;
            border: 1px solid transparent;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
            transition: transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease;
        }

        .card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 28px rgba(0,0,0,0.4);
            border-color: #334155;
        }

        .place-title {
            font-size: 20px;
            font-weight: 600;
            color: #38bdf8;
        }

        .address {
            font-size: 13px;
            color: #cbd5e1;
            margin-bottom: 10px;
        }

        .desc {
            font-size: 14px;
            color: #e2e8f0;
        }

        /* Big call-to-action buttons (Create my itinerary / Generate plan / Plan another trip) */
        div[data-testid="stButton"] button[kind="primary"] {
            width: 100%;
            font-size: 18px;
            font-weight: 700;
            padding: 0.75em 1.5em;
            border-radius: 12px;
            border: none;
            background: linear-gradient(135deg, #38bdf8, #6366f1);
            color: white;
            box-shadow: 0 4px 14px rgba(56, 189, 248, 0.35);
            transition: transform 0.15s ease, box-shadow 0.15s ease;
        }

        div[data-testid="stButton"] button[kind="primary"]:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(99, 102, 241, 0.45);
            color: white;
        }

        /* Quick-reply suggestion chips */
        div[data-testid="stButton"] button[kind="secondary"] {
            border-radius: 999px;
            border: 1px solid #334155;
            background: #1e293b;
            color: #cbd5e1;
            font-size: 13px;
            padding: 0.25em 0.9em;
            transition: all 0.15s ease;
        }

        div[data-testid="stButton"] button[kind="secondary"]:hover {
            border-color: #38bdf8;
            color: #38bdf8;
        }
    </style>
    """, unsafe_allow_html=True)
