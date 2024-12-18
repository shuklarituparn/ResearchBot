import os
from dotenv import load_dotenv
from langchain_community.tools.tavily_search import TavilySearchResults

from bot.utils import translate, translate_english

load_dotenv()
"""Загружаем Ключи Доступа"""
TOKEN = os.getenv("GIGACHAT_API_AUTH")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")


async def ai_help(query):
    tavily_tool = TavilySearchResults(max_results=1)
    tools = [tavily_tool]
    response = tavily_tool.invoke({"query": query})
    print(response)
    result = response[0]["content"]
    result_to_send = await translate.translate_text(result)
    return result_to_send
