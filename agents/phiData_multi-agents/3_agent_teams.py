from datetime import date
import datetime
import os
from phi.agent import Agent
from phi.model.groq import Groq
from phi.model.openai import OpenAIChat
from phi.tools.yfinance import YFinanceTools
from phi.tools.duckduckgo import DuckDuckGo
from dotenv import load_dotenv

# Attribution: https://github.com/codebasics/ai-agents/blob/main/1_phidata_finance_agent/2_finance_agent_llama.py

# Delete environment variables if it already exists
if "OPENAI_API_KEY" in os.environ:
    del os.environ["OPENAI_API_KEY"]

# Load environment variables
load_dotenv()

web_agent = Agent(
    # model = Groq(id="llama-3.3-70b-versatile"),
    name="Web Agent",
    model = OpenAIChat(id="gpt-4o"),
    tools = [
        DuckDuckGo()
    ],
    instructions=["Always include sources in your responses."],
    show_tool_calls=True,
    markdown=True,
    debug_mode=False,
)

finance_agent = Agent(
    # model = Groq(id="llama-3.3-70b-versatile"),
    name ="Finance Agent", 
    role = "Get Financial Data",
    model = OpenAIChat(id="gpt-4o"),
    tools = [
        YFinanceTools(stock_price=True, analyst_recommendations=True, stock_fundamentals=True)    
    ],
    instructions=["Use tables to display data.",
    "If you need to find the symbol for a company, use the get_company_symbol tool."],
    show_tool_calls=True,
    markdown=True,
    debug_mode=False,
)

agent_team = Agent(
    team = [web_agent, finance_agent],
    instructions=[
        "Always include sources in your responses.",
        "Use tables to display data."
    ],
    show_tool_calls=True,
    markdown=True,
    debug_mode=False,
)

agent_team.print_response(
    "Summarize analyst recommendations share the latest news for NVDA.", 
    stream=True
)