import os
import requests
import streamlit as st

st.set_page_config(page_title="Personal Chatbot", page_icon=":robot_face:", layout="wide")

API_URL = os.environ.get("API_URL", "http://127.0.0.1:9999/chat").strip()
MODELNAMES_GROQ = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]
MODEL_NAMES_OPENAI = ["gpt-4o-mini"]

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@700&display=swap');

    /* ── Base layout ── */
    .block-container {
        padding-top: 2.5rem !important;
        padding-bottom: 1rem;
        max-width: 1100px;
    }

    /* ── Header ── */
    .app-header {
        background: transparent;
        padding: 8px 4px;
        margin-bottom: 4px;
    }
    .header-inner {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
    }
    .header-title {
        flex: 1;
        text-align: center;
    }
    .header-title h1 {
        font-family: 'Cinzel Decorative', cursive;
        font-size: 1.8rem;
        font-weight: 700;
        margin: 0;
        background: linear-gradient(90deg, #3730a3 0%, #7c3aed 45%, #4f46e5 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: 0.04em;
        filter: drop-shadow(0 0 14px rgba(124, 58, 237, 0.35));
    }

    /* ── Left orb animation (inline in header) ── */
    .loader-wrapper {
        position: relative;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
        width: 90px;
        height: 90px;
        font-family: "Inter", sans-serif;
        font-size: 0.6em;
        font-weight: 300;
        color: white;
        border-radius: 50%;
        user-select: none;
        letter-spacing: 1px;
    }
    .loader {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        aspect-ratio: 1 / 1;
        border-radius: 50%;
        background-color: transparent;
        animation: loader-rotate 2s linear infinite;
        z-index: 0;
    }
    @keyframes loader-rotate {
        0% {
            transform: rotate(90deg);
            box-shadow:
                0 10px 20px 0 #fff inset,
                0 20px 30px 0 #ad5fff inset,
                0 60px 60px 0 #471eec inset;
        }
        50% {
            transform: rotate(270deg);
            box-shadow:
                0 10px 20px 0 #fff inset,
                0 20px 10px 0 #d60a47 inset,
                0 40px 60px 0 #311e80 inset;
        }
        100% {
            transform: rotate(450deg);
            box-shadow:
                0 10px 20px 0 #fff inset,
                0 20px 30px 0 #ad5fff inset,
                0 60px 60px 0 #471eec inset;
        }
    }
    .loader-letter {
        display: inline-block;
        opacity: 0.4;
        transform: translateY(0);
        animation: loader-letter-anim 2s infinite;
        z-index: 1;
    }
    .loader-letter:nth-child(1)  { animation-delay: 0.0s; }
    .loader-letter:nth-child(2)  { animation-delay: 0.1s; }
    .loader-letter:nth-child(3)  { animation-delay: 0.2s; }
    .loader-letter:nth-child(4)  { animation-delay: 0.3s; }
    .loader-letter:nth-child(5)  { animation-delay: 0.4s; }
    .loader-letter:nth-child(6)  { animation-delay: 0.5s; }
    .loader-letter:nth-child(7)  { animation-delay: 0.6s; }
    .loader-letter:nth-child(8)  { animation-delay: 0.7s; }
    .loader-letter:nth-child(9)  { animation-delay: 0.8s; }
    .loader-letter:nth-child(10) { animation-delay: 0.9s; }
    @keyframes loader-letter-anim {
        0%, 100% { opacity: 0.4; transform: translateY(0); }
        20%       { opacity: 1;   transform: scale(1.15);  }
        40%       { opacity: 0.7; transform: translateY(0); }
    }

    /* ── Right hamster animation (inline in header) ── */
    .hamster-wrapper {
        flex-shrink: 0;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .hamster-wrapper .wheel-and-hamster {
        --dur: 1s;
        position: relative;
        width: 12em;
        height: 12em;
        font-size: 8px;
    }
    .hamster-wrapper .wheel,
    .hamster-wrapper .hamster,
    .hamster-wrapper .hamster div,
    .hamster-wrapper .spoke {
        position: absolute;
    }
    .hamster-wrapper .wheel,
    .hamster-wrapper .spoke {
        border-radius: 50%;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
    }
    .hamster-wrapper .wheel {
        background: radial-gradient(
            100% 100% at center,
            hsla(0,0%,60%,0) 47.8%,
            hsl(0,0%,60%) 48%
        );
        z-index: 2;
    }
    .hamster-wrapper .hamster {
        animation: hamster var(--dur) ease-in-out infinite;
        top: 50%;
        left: calc(50% - 3.5em);
        width: 7em;
        height: 3.75em;
        transform: rotate(4deg) translate(-0.8em,1.85em);
        transform-origin: 50% 0;
        z-index: 1;
    }
    .hamster-wrapper .hamster__head {
        animation: hamsterHead var(--dur) ease-in-out infinite;
        background: hsl(30,90%,55%);
        border-radius: 70% 30% 0 100% / 40% 25% 25% 60%;
        box-shadow:
            0 -0.25em 0 hsl(30,90%,80%) inset,
            0.75em -1.55em 0 hsl(30,90%,90%) inset;
        top: 0;
        left: -2em;
        width: 2.75em;
        height: 2.5em;
        transform-origin: 100% 50%;
    }
    .hamster-wrapper .hamster__ear {
        animation: hamsterEar var(--dur) ease-in-out infinite;
        background: hsl(0,90%,85%);
        border-radius: 50%;
        box-shadow: -0.25em 0 hsl(30,90%,55%) inset;
        top: -0.25em;
        right: -0.25em;
        width: 0.75em;
        height: 0.75em;
        transform-origin: 50% 75%;
    }
    .hamster-wrapper .hamster__eye {
        animation: hamsterEye var(--dur) linear infinite;
        background-color: black;
        border-radius: 50%;
        top: 0.375em;
        left: 1.25em;
        width: 0.5em;
        height: 0.5em;
    }
    .hamster-wrapper .hamster__nose {
        background: hsl(0,90%,75%);
        border-radius: 35% 65% 85% 15% / 70% 50% 50% 30%;
        top: 0.75em;
        left: 0;
        width: 0.2em;
        height: 0.25em;
    }
    .hamster-wrapper .hamster__body {
        animation: hamsterBody var(--dur) ease-in-out infinite;
        background: hsl(30,90%,90%);
        border-radius: 50% 30% 50% 30% / 15% 60% 40% 40%;
        box-shadow:
            0.1em 0.75em 0 hsl(30,90%,55%) inset,
            0.15em -0.5em 0 hsl(30,90%,80%) inset;
        top: 0.25em;
        left: 2em;
        width: 4.5em;
        height: 3em;
        transform-origin: 17% 50%;
        transform-style: preserve-3d;
    }
    .hamster-wrapper .hamster__limb--fr,
    .hamster-wrapper .hamster__limb--fl {
        clip-path: polygon(0 0,100% 0,70% 80%,60% 100%,0% 100%,40% 80%);
        top: 2em;
        left: 0.5em;
        width: 1em;
        height: 1.5em;
        transform-origin: 50% 0;
    }
    .hamster-wrapper .hamster__limb--fr {
        animation: hamsterFRLimb var(--dur) linear infinite;
        background: linear-gradient(hsl(30,90%,80%) 80%,hsl(0,90%,75%) 80%);
        transform: rotate(15deg) translateZ(-1px);
    }
    .hamster-wrapper .hamster__limb--fl {
        animation: hamsterFLLimb var(--dur) linear infinite;
        background: linear-gradient(hsl(30,90%,90%) 80%,hsl(0,90%,85%) 80%);
        transform: rotate(15deg);
    }
    .hamster-wrapper .hamster__limb--br,
    .hamster-wrapper .hamster__limb--bl {
        border-radius: 0.75em 0.75em 0 0;
        clip-path: polygon(0 0,100% 0,100% 30%,70% 90%,70% 100%,30% 100%,40% 90%,0% 30%);
        top: 1em;
        left: 2.8em;
        width: 1.5em;
        height: 2.5em;
        transform-origin: 50% 30%;
    }
    .hamster-wrapper .hamster__limb--br {
        animation: hamsterBRLimb var(--dur) linear infinite;
        background: linear-gradient(hsl(30,90%,80%) 90%,hsl(0,90%,75%) 90%);
        transform: rotate(-25deg) translateZ(-1px);
    }
    .hamster-wrapper .hamster__limb--bl {
        animation: hamsterBLLimb var(--dur) linear infinite;
        background: linear-gradient(hsl(30,90%,90%) 90%,hsl(0,90%,85%) 90%);
        transform: rotate(-25deg);
    }
    .hamster-wrapper .hamster__tail {
        animation: hamsterTail var(--dur) linear infinite;
        background: hsl(0,90%,85%);
        border-radius: 0.25em 50% 50% 0.25em;
        box-shadow: 0 -0.2em 0 hsl(0,90%,75%) inset;
        top: 1.5em;
        right: -0.5em;
        width: 1em;
        height: 0.5em;
        transform: rotate(30deg) translateZ(-1px);
        transform-origin: 0.25em 0.25em;
    }
    .hamster-wrapper .spoke {
        animation: spoke var(--dur) linear infinite;
        background:
            radial-gradient(
                100% 100% at center,
                hsl(0,0%,60%) 4.8%,
                hsla(0,0%,60%,0) 5%
            ),
            linear-gradient(
                hsla(0,0%,55%,0) 46.9%,
                hsl(0,0%,65%) 47% 52.9%,
                hsla(0,0%,65%,0) 53%
            ) 50% 50% / 99% 99% no-repeat;
    }
    @keyframes hamster {
        from, to { transform: rotate(4deg) translate(-0.8em,1.85em); }
        50%       { transform: rotate(0) translate(-0.8em,1.85em); }
    }
    @keyframes hamsterHead {
        from,25%,50%,75%,to      { transform: rotate(0); }
        12.5%,37.5%,62.5%,87.5% { transform: rotate(8deg); }
    }
    @keyframes hamsterEye {
        from,90%,to { transform: scaleY(1); }
        95%         { transform: scaleY(0); }
    }
    @keyframes hamsterEar {
        from,25%,50%,75%,to      { transform: rotate(0); }
        12.5%,37.5%,62.5%,87.5% { transform: rotate(12deg); }
    }
    @keyframes hamsterBody {
        from,25%,50%,75%,to      { transform: rotate(0); }
        12.5%,37.5%,62.5%,87.5% { transform: rotate(-2deg); }
    }
    @keyframes hamsterFRLimb {
        from,25%,50%,75%,to      { transform: rotate(50deg) translateZ(-1px); }
        12.5%,37.5%,62.5%,87.5% { transform: rotate(-30deg) translateZ(-1px); }
    }
    @keyframes hamsterFLLimb {
        from,25%,50%,75%,to      { transform: rotate(-30deg); }
        12.5%,37.5%,62.5%,87.5% { transform: rotate(50deg); }
    }
    @keyframes hamsterBRLimb {
        from,25%,50%,75%,to      { transform: rotate(-60deg) translateZ(-1px); }
        12.5%,37.5%,62.5%,87.5% { transform: rotate(20deg) translateZ(-1px); }
    }
    @keyframes hamsterBLLimb {
        from,25%,50%,75%,to      { transform: rotate(20deg); }
        12.5%,37.5%,62.5%,87.5% { transform: rotate(-60deg); }
    }
    @keyframes hamsterTail {
        from,25%,50%,75%,to      { transform: rotate(30deg) translateZ(-1px); }
        12.5%,37.5%,62.5%,87.5% { transform: rotate(10deg) translateZ(-1px); }
    }
    @keyframes spoke {
        from { transform: rotate(0); }
        to   { transform: rotate(-1turn); }
    }

    /* ── Tablet (≤ 768px) ── */
    @media (max-width: 768px) {
        .block-container {
            padding-top: 3rem !important;
            padding-left: 0.75rem !important;
            padding-right: 0.75rem !important;
            max-width: 100% !important;
        }
        .app-header { padding: 6px 4px; }
        .header-title h1 { font-size: 1.3rem; }
        .loader-wrapper  { width: 70px; height: 70px; font-size: 0.5em; }
        .hamster-wrapper .wheel-and-hamster { font-size: 6px; }
    }

    /* ── Mobile (≤ 480px) ── */
    @media (max-width: 480px) {
        .block-container {
            padding-top: 3.5rem !important;
            padding-left: 0.5rem !important;
            padding-right: 0.5rem !important;
        }
        .app-header { padding: 4px 2px; }
        .header-inner { gap: 6px; }
        .header-title h1 { font-size: 1rem; letter-spacing: 0.02em; }
        .loader-wrapper  { width: 54px; height: 54px; font-size: 0.42em; }
        .hamster-wrapper .wheel-and-hamster { font-size: 5px; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="app-header">
        <div class="header-inner">
            <div class="loader-wrapper">
                <span class="loader-letter">C</span>
                <span class="loader-letter">h</span>
                <span class="loader-letter">a</span>
                <span class="loader-letter">t</span>
                <span class="loader-letter">&nbsp;</span>
                <span class="loader-letter">B</span>
                <span class="loader-letter">o</span>
                <span class="loader-letter">t</span>
                <div class="loader"></div>
            </div>
            <div class="header-title">
                <h1>Personal Chatbot</h1>
            </div>
            <div class="hamster-wrapper">
                <div aria-label="Hamster running in a wheel" role="img" class="wheel-and-hamster">
                    <div class="wheel"></div>
                    <div class="hamster">
                        <div class="hamster__body">
                            <div class="hamster__head">
                                <div class="hamster__ear"></div>
                                <div class="hamster__eye"></div>
                                <div class="hamster__nose"></div>
                            </div>
                            <div class="hamster__limb hamster__limb--fr"></div>
                            <div class="hamster__limb hamster__limb--fl"></div>
                            <div class="hamster__limb hamster__limb--br"></div>
                            <div class="hamster__limb hamster__limb--bl"></div>
                            <div class="hamster__tail"></div>
                        </div>
                    </div>
                    <div class="spoke"></div>
                </div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.subheader("Agent Settings")
    provider = st.radio("Model provider", options=["Groq", "OpenAI"], horizontal=True)
    if provider == "Groq":
        model_name = st.selectbox("Model", options=MODELNAMES_GROQ)
    else:
        model_name = st.selectbox("Model", options=MODEL_NAMES_OPENAI)
    allow_search = st.toggle("Enable web search", value=False)
    system_prompt = st.text_area(
        "System prompt",
        height=120,
        placeholder="Define your AI agent's behavior...",
        value="Act as an AI chatbot who is smart and friendly",
    )
    if st.button("Clear chat"):
        st.session_state.chat_history = []
        st.rerun()

for item in st.session_state.chat_history:
    with st.chat_message(item["role"]):
        st.markdown(item["content"])

user_query = st.chat_input("Ask anything...")

if user_query:
    st.session_state.chat_history.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    payload = {
        "model_name": model_name,
        "model_provider": provider,
        "system_prompt": system_prompt,
        "messages": [user_query],
        "allow_search": allow_search,
    }

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(API_URL, json=payload, timeout=120)
                if response.status_code == 200:
                    response_data = response.json()
                    if isinstance(response_data, dict) and "response" in response_data:
                        assistant_text = response_data["response"]
                        st.markdown(assistant_text)
                        st.session_state.chat_history.append(
                            {"role": "assistant", "content": assistant_text}
                        )
                    else:
                        st.error("Unexpected response format from backend.")
                        st.write(response_data)
                else:
                    try:
                        err = response.json()
                    except Exception:
                        err = response.text
                    st.error(f"Backend error ({response.status_code}): {err}")
            except requests.RequestException as exc:
                st.error(f"Request failed: {exc}")
