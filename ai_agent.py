import os
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.prebuilt import create_react_agent
from langchain_core.messages.ai import AIMessage


openai_llm = ChatOpenAI(model="gpt-4o-mini")
groq_llm = ChatGroq(model="llama-3.3-70b-versatile")

search_tool = TavilySearchResults(max_results=2)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

system_prompt = "Act as an AI chatbot who is smart and friendly"

agent = create_react_agent(
    model = groq_llm,
    tools = [search_tool],
    prompt = system_prompt
)

query="What are the latest advancements in AI research?"
state={"messages":query}
response = agent.invoke(state)
messages = response.get("messages")
ai_messages = [message.content for message in messages if isinstance(message, AIMessage)]
print(ai_messages[-1])