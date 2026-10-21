# agent/graph.py
import os
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from .prompts import SYSTEM_PROMPT

load_dotenv()


def _build_client() -> MultiServerMCPClient:
    """创建 MCP 客户端，指向两个本地 MCP 服务器。"""
    return MultiServerMCPClient(
        {
            "weather": {
                "command": "python",
                "args": ["servers/weather_server.py"],
                "transport": "stdio",
                "cwd": os.getcwd(),
            },
            "travel": {
                "command": "python",
                "args": ["servers/travel_server.py"],
                "transport": "stdio",
                "cwd": os.getcwd(),
            },
        }
    )


async def build_agent():
    """异步构建 ReAct Agent，返回 (agent, tools)。"""
    llm = ChatOpenAI(
        model=os.getenv("LLM_MODEL", "deepseek-chat"),
        api_key=os.getenv("LLM_API_KEY"),
        base_url=os.getenv("LLM_BASE_URL", "https://api.deepseek.com"),
        temperature=0,
    )

    client = _build_client()
    tools = await client.get_tools()

    agent = create_react_agent(
        model=llm,
        tools=tools,
        prompt=SYSTEM_PROMPT,
    )
    return agent, tools