from pydantic import BaseModel
from typing import List

class RequestState(BaseModel):
    model_name: str
    model_provider: str
    system_prompt: str
    messages: list[str]
    allow_search: bool



from fastapi import FastAPI
from ai_agent import get_response_from_ai_agent

ALLOWED_MODEL_NAMES = ["llama3-70b-8192","mixtral-87b-32768","gpt-4o-mini", "llama-3.3-70b-versatile"]

app=FastAPI(title= "LangGraph AI Agent Chatbot")

@app.post("/chat")
def chat_endpoint(request: RequestState):
    """
    API Endpoint to interact with the chatbot using LangGraph and search tools.
    """
    if request.model_name not in ALLOWED_MODEL_NAMES:
        return {"error": f"Invalid model name. Allowed models: {ALLOWED_MODEL_NAMES}"}