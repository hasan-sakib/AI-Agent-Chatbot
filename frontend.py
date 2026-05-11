import streamlit as st
import os

st.set_page_config(page_title="LangGraph AI Agent", page_icon=":robot_face:")   
st.title("LangGraph AI Agent Chatbot")
st.write("This is a chatbot that uses the LangGraph AI Agent to answer your questions.")
system_prompt = st.text_area("Define your AI Agent: ",height=70,placeholder="Type your system prompt here..")

MODELNAMES_GROQ = ["mixtral-8x7b-32768", "llama-3.3-70b-versatile"]
MODEL_NAMES_OPENAI = ["gpt-4o-mini"]

provider=st.radio("Select a model provider: ", options=["Groq", "OpenAI"])

if provider == "Groq":
    model_name = st.selectbox("Select a model: ", options=MODELNAMES_GROQ)
elif provider == "OpenAI":
    model_name = st.selectbox("Select a model: ", options=MODEL_NAMES_OPENAI)



allow_search = st.checkbox("Allow search? (Useful for complex questions)")

user_query = st.text_area("Enter your query: ",height=70,placeholder="Ask anything")

API_URL = os.environ.get("API_URL", "http://127.0.0.1:9999/chat").strip()

if st.button("Ask Agent"):
    if user_query.strip():
        import requests
        payload = {
            "model_name": model_name,
            "model_provider": provider,
            "system_prompt": system_prompt,
            "messages": [user_query],
            "allow_search": allow_search
        }
        response = requests.post(API_URL, json=payload)
        if response.status_code == 200:
            response_data = response.json()
            if isinstance(response_data, dict) and "response" in response_data:
                st.header("Agent Response:")
                st.markdown(response_data["response"])
            else:
                st.error("Unexpected response format from backend.")
                st.write(response_data)
        else:
            try:
                err = response.json()
            except Exception:
                err = response.text
            st.error(f"Backend error ({response.status_code}): {err}")


