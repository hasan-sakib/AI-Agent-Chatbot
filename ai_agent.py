# if you dont use pipenv uncomment the following:
# from dotenv import load_dotenv
# load_dotenv()

#Step1: Setup API Keys for Groq, OpenAI and Tavily
import os

GROQ_API_KEY=os.environ.get("GROQ_API_KEY")
TAVILY_API_KEY=os.environ.get("TAVILY_API_KEY")
OPENAI_API_KEY=os.environ.get("OPENAI_API_KEY")

#Step2: Setup LLM & Tools
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults

#Step3: Setup AI Agent with Search tool functionality
from langgraph.prebuilt import create_react_agent
from langchain_core.messages.ai import AIMessage

system_prompt="Act as an AI chatbot who is smart and friendly"

def _chat_model_for_provider(provider, llm_id):
    p = str(provider or "").strip().casefold()
    if p == "groq":
        return ChatGroq(model=llm_id)
    if p == "openai":
        return ChatOpenAI(model=llm_id)
    raise ValueError(
        f"Unknown model_provider {provider!r}; use 'Groq' or 'OpenAI'."
    )


def get_response_from_ai_agent(llm_id, query, allow_search, system_prompt, provider):
    chat_model = _chat_model_for_provider(provider, llm_id)
    if not isinstance(query, list) or not query:
        raise ValueError("messages must be a non-empty list of strings.")
    prompt = "\n".join(str(message).strip() for message in query if str(message).strip())
    if not prompt:
        raise ValueError("messages must contain at least one non-empty string.")

    tools=[TavilySearchResults(max_results=2)] if allow_search else []
    agent=create_react_agent(
        model=chat_model,
        tools=tools,
        prompt=system_prompt
    )
    state={"messages": [{"role": "user", "content": prompt}]}
    response=agent.invoke(state)
    messages=response.get("messages")
    ai_messages=[message.content for message in messages if isinstance(message, AIMessage)]
    return ai_messages[-1]