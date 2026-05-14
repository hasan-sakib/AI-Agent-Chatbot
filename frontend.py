import os
import requests
import streamlit as st

st.set_page_config(page_title="AI Agent Chatbot", page_icon=":robot_face:", layout="wide")

API_URL = os.environ.get("API_URL", "http://127.0.0.1:9999/chat").strip()
MODELNAMES_GROQ = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]
MODEL_NAMES_OPENAI = ["gpt-4o-mini"]

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1.25rem;
        padding-bottom: 1rem;
        max-width: 1100px;
    }
    .app-header {
        background: linear-gradient(120deg, #312e81 0%, #4f46e5 42%, #7c3aed 100%);
        border-radius: 16px;
        padding: 20px 24px;
        color: #ffffff;
        margin-bottom: 12px;
        box-shadow: 0 12px 28px rgba(49, 46, 129, 0.28);
    }
    .app-header h2 {
        margin: 0 0 8px 0;
        font-size: 1.55rem;
    }
    .app-header p {
        margin: 0;
        opacity: 0.92;
    }

    /* Generating loader — fixed top-left */
    .loader-wrapper {
        position: fixed;
        top: 12px;
        left: 70px;
        display: flex;
        align-items: center;
        justify-content: center;
        width: 110px;
        height: 110px;
        font-family: "Inter", sans-serif;
        font-size: 0.65em;
        font-weight: 300;
        color: white;
        border-radius: 50%;
        user-select: none;
        z-index: 2147483647;
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
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="loader-wrapper">
        <span class="loader-letter">G</span>
        <span class="loader-letter">e</span>
        <span class="loader-letter">n</span>
        <span class="loader-letter">e</span>
        <span class="loader-letter">r</span>
        <span class="loader-letter">a</span>
        <span class="loader-letter">t</span>
        <span class="loader-letter">i</span>
        <span class="loader-letter">n</span>
        <span class="loader-letter">g</span>
        <div class="loader"></div>
    </div>
    <div class="app-header">
        <h2>LangGraph AI Agent Chatbot</h2>
        <p>Ask questions, enable live search when needed, and tune model behavior from the sidebar.</p>
    </div>
    """,
    unsafe_allow_html=True,
)
st.caption(f"Connected backend: `{API_URL}`")

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
