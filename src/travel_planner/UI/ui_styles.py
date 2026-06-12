import streamlit as st


def apply_custom_css():
    st.markdown("""
    <style>
        :root {
            --ease-apple: cubic-bezier(0.16, 1, 0.3, 1);
        }

        html {
            scroll-behavior: smooth;
        }

        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(18px); }
            to { opacity: 1; transform: translateY(0); }
        }

        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }

        @keyframes gradientFlow {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        @keyframes floatBlobA {
            0%, 100% { transform: translate(-8%, -6%) scale(1); }
            50% { transform: translate(8%, 6%) scale(1.15); }
        }

        @keyframes floatBlobB {
            0%, 100% { transform: translate(6%, 8%) scale(1); }
            50% { transform: translate(-8%, -6%) scale(1.2); }
        }

        @keyframes pulseDot {
            0%, 80%, 100% { transform: scale(0.6); opacity: 0.35; }
            40% { transform: scale(1); opacity: 1; }
        }

        /* Soft, slowly drifting gradient blobs behind the whole app */
        [data-testid="stAppViewContainer"] {
            position: relative;
            overflow: hidden;
            background-color: #0f172a;
        }

        [data-testid="stAppViewContainer"]::before,
        [data-testid="stAppViewContainer"]::after {
            content: "";
            position: fixed;
            border-radius: 50%;
            filter: blur(100px);
            opacity: 0.28;
            pointer-events: none;
            z-index: 0;
        }

        [data-testid="stAppViewContainer"]::before {
            width: 50vw;
            height: 50vw;
            top: -15%;
            left: -15%;
            background: radial-gradient(circle, #38bdf8, transparent 70%);
            animation: floatBlobA 24s ease-in-out infinite;
        }

        [data-testid="stAppViewContainer"]::after {
            width: 55vw;
            height: 55vw;
            bottom: -20%;
            right: -15%;
            background: radial-gradient(circle, #818cf8, transparent 70%);
            animation: floatBlobB 28s ease-in-out infinite;
        }

        [data-testid="stAppViewContainer"] > .main {
            position: relative;
            z-index: 1;
        }

        .main {
            background-color: transparent;
            color: white;
        }

        .title {
            text-align: center;
            font-size: 44px;
            font-weight: 800;
            margin-bottom: 6px;
            background: linear-gradient(135deg, #38bdf8, #818cf8, #38bdf8);
            background-size: 200% auto;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            animation: gradientFlow 6s ease infinite, fadeInUp 0.7s var(--ease-apple) both;
        }

        .subtitle {
            text-align: center;
            color: #94a3b8;
            margin-bottom: 30px;
            font-size: 16px;
            animation: fadeInUp 0.7s var(--ease-apple) both;
            animation-delay: 0.08s;
        }

        h3, h4 {
            animation: fadeInUp 0.5s var(--ease-apple) both;
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
            transition: transform 0.25s var(--ease-apple), box-shadow 0.25s var(--ease-apple), border-color 0.25s var(--ease-apple);
            animation: fadeInUp 0.5s var(--ease-apple) both;
        }

        .card:hover {
            transform: translateY(-3px) scale(1.01);
            box-shadow: 0 10px 30px rgba(0,0,0,0.4);
            border-color: #38bdf8;
        }

        .place-title {
            font-size: 20px;
            font-weight: 600;
            color: #38bdf8;
        }

        .marker-badge {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            min-width: 24px;
            height: 24px;
            padding: 0 6px;
            border-radius: 999px;
            background: linear-gradient(135deg, #38bdf8, #6366f1);
            color: white;
            font-size: 13px;
            font-weight: 700;
            margin-right: 8px;
            vertical-align: middle;
            animation: fadeIn 0.4s ease both;
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

        /* Question cards fade/slide in, with a gentle staggered feel and a
           glowing hover border to invite interaction */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            border-radius: 16px !important;
            animation: fadeInUp 0.5s var(--ease-apple) both;
            transition: border-color 0.3s var(--ease-apple), box-shadow 0.3s var(--ease-apple), transform 0.3s var(--ease-apple);
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:hover {
            border-color: #38bdf8 !important;
            box-shadow: 0 8px 24px rgba(56, 189, 248, 0.15);
            transform: translateY(-2px);
        }

        /* Big call-to-action buttons (Create my itinerary / Generate plan / Plan another trip) */
        div[data-testid="stButton"] button[kind="primary"] {
            width: 100%;
            font-size: 18px;
            font-weight: 700;
            padding: 0.75em 1.5em;
            border-radius: 12px;
            border: none;
            background: linear-gradient(135deg, #38bdf8, #6366f1, #38bdf8);
            background-size: 200% auto;
            background-position: 0% 0;
            color: white;
            box-shadow: 0 4px 14px rgba(56, 189, 248, 0.35);
            transition: transform 0.25s var(--ease-apple), box-shadow 0.25s var(--ease-apple), background-position 0.6s var(--ease-apple);
        }

        div[data-testid="stButton"] button[kind="primary"]:hover {
            transform: translateY(-2px) scale(1.01);
            box-shadow: 0 6px 22px rgba(99, 102, 241, 0.45);
            background-position: 100% 0;
            color: white;
        }

        div[data-testid="stButton"] button[kind="primary"]:active {
            transform: translateY(0) scale(0.97);
            transition-duration: 0.1s;
        }

        /* Quick-reply suggestion chips */
        div[data-testid="stButton"] button[kind="secondary"] {
            border-radius: 999px;
            border: 1px solid #334155;
            background: #1e293b;
            color: #cbd5e1;
            font-size: 13px;
            padding: 0.25em 0.9em;
            transition: transform 0.2s var(--ease-apple), border-color 0.2s var(--ease-apple), color 0.2s var(--ease-apple), box-shadow 0.2s var(--ease-apple);
        }

        div[data-testid="stButton"] button[kind="secondary"]:hover {
            border-color: #38bdf8;
            color: #38bdf8;
            transform: translateY(-1px) scale(1.04);
            box-shadow: 0 4px 14px rgba(56, 189, 248, 0.2);
        }

        div[data-testid="stButton"] button[kind="secondary"]:active {
            transform: scale(0.95);
            transition-duration: 0.1s;
        }

        /* Friendly animated "thinking" indicator while a plan is generated */
        .loading-wrap {
            display: flex;
            align-items: center;
            gap: 10px;
            color: #94a3b8;
            font-size: 15px;
            margin: 14px 0;
            animation: fadeIn 0.4s ease both;
        }

        .loading-dots {
            display: inline-flex;
            gap: 4px;
        }

        .loading-dots span {
            width: 7px;
            height: 7px;
            border-radius: 50%;
            background: linear-gradient(135deg, #38bdf8, #6366f1);
            animation: pulseDot 1.2s ease-in-out infinite;
        }

        .loading-dots span:nth-child(2) { animation-delay: 0.15s; }
        .loading-dots span:nth-child(3) { animation-delay: 0.3s; }

        div[data-testid="stSpinner"] {
            animation: fadeIn 0.3s ease both;
            color: #94a3b8;
        }

        /* Smooth, slide-in feel for the map */
        [data-testid="stDeckGlJsonChart"] {
            animation: fadeInUp 0.6s var(--ease-apple) both;
            border-radius: 16px;
            overflow: hidden;
        }

        .block-container {
            padding-bottom: 56px;
        }

        .footer {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            text-align: center;
            color: #64748b;
            font-size: 12px;
            padding: 10px 0;
            background: rgba(15, 23, 42, 0.85);
            backdrop-filter: blur(8px);
            border-top: 1px solid #1e293b;
            z-index: 10;
            animation: fadeIn 0.8s ease both;
        }
    </style>
    """, unsafe_allow_html=True)
