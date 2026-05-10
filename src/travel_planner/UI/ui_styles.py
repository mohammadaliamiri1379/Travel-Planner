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
            font-size: 42px;
            font-weight: 700;
            margin-bottom: 10px;
        }

        .subtitle {
            text-align: center;
            color: #94a3b8;
            margin-bottom: 30px;
        }

        .card {
            background: #1e293b;
            padding: 20px;
            border-radius: 16px;
            margin-bottom: 15px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
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

        .btn {
            width: 100%;
        }
    </style>
    """, unsafe_allow_html=True)