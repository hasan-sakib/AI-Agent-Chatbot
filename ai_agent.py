import os
from langchain_groq import chatGroq
from langchain_openai import chatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.prebuilt import create_react_agent


openai_llm = chatOpenAI(model="gpt-4o-mini", temperature=0.7)
groq_llm = chatGroq(model="llama-3.3-70b-versatile")

search_tool = TavilySearchResults(max_results=2)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

system_prompt = """You are an assistant for a user who is looking for information on the internet. You have access to a search tool that can help you find relevant information. Use the search tool to find the information you need to answer the user's question. Be concise and provide accurate information based on the search results."""

agent = create_react_agent(
    llm = groq_llm,
    tools = [search_tool],
    state_modifier = system_prompt
)

query="What are the latest advancements in AI research?"
state={"messages":query}
response = agent.invoke(state)