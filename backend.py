from dotenv import load_dotenv
load_dotenv()

from pydantic import BaseModel
from typing import List

class RequestState(BaseModel):
    model_name: str
    model_provider: str
    system_prompt: str
    messages: List[str]
    allow_search: bool

from fastapi import FastAPI, HTTPException
from ai_agent import get_response_from_ai_agent

ALLOWED_MODELS_BY_PROVIDER = {
    "groq": {"llama-3.3-70b-versatile", "llama-3.1-8b-instant"},
    "openai": {"gpt-4o-mini"},
}
ALLOWED_PROVIDERS = {"groq", "openai"}

app = FastAPI(title="LangGraph AI Agent")


@app.post("/chat")
def chat_endpoint(request: RequestState):
    provider = (request.model_provider or "").strip().casefold()
    if provider not in ALLOWED_PROVIDERS:
        raise HTTPException(status_code=400, detail="Invalid model_provider. Use 'Groq' or 'OpenAI'.")
    if request.model_name not in ALLOWED_MODELS_BY_PROVIDER[provider]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid model_name for provider '{request.model_provider}'.",
        )
    if not request.messages:
        raise HTTPException(status_code=400, detail="messages cannot be empty.")

    try:
        response = get_response_from_ai_agent(
            request.model_name,
            request.messages,
            request.allow_search,
            request.system_prompt,
            request.model_provider,
        )
        return {"response": response}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Internal server error: {exc}") from exc


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=9999)
