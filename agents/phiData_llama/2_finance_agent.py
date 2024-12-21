from datetime import date
import datetime
import os
from phi.agent import Agent
from phi.model.groq import Groq
from phi.model.openai import OpenAIChat
from phi.tools.yfinance import YFinanceTools
from dotenv import load_dotenv

# Attribution: https://github.com/codebasics/ai-agents/blob/main/1_phidata_finance_agent/2_finance_agent_llama.py

# Delete environment variables if needed
if "OPENAI_API_KEY" in os.environ:
    del os.environ["OPENAI_API_KEY"]

load_dotenv()

def get_company_symbol(company: str) -> str:
    """Use this function to get the symbol for a company.

    Args:
        company (str): The name of the company.

    Returns:
        str: The symbol for the company.
    """
    symbols = {
        "Phidata": "MSFT",
        "Infosys": "INFY",
        "Tesla": "TSLA",
        "Apple": "AAPL",
        "Microsoft": "MSFT",
        "Amazon": "AMZN",
        "Google": "GOOGL",
    }
    return symbols.get(company, "Unknown")

finance_agent = Agent(
    # model = Groq(id="llama-3.3-70b-versatile"),
    model = OpenAIChat(id="gpt-4"),
    tools = [
        YFinanceTools(stock_price=True, analyst_recommendations=True, stock_fundamentals=True),
        get_company_symbol # Example custom tool
    ],
    instructions=["Use tables to display data.",
    "If you need to find the symbol for a company, use the get_company_symbol tool."],
    show_tool_calls=True,
    markdown=True,
    debug_mode=False,
)

finance_agent.print_response(
    "Summarize and compare analyst recommendations and fundamentals for TSLA and Phidata. Show in tables.", 
    stream=True
)