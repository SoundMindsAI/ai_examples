# AI Agents with Phidata

This project demonstrates the implementation of AI agents using the Phidata framework, showcasing different agent configurations and capabilities for financial analysis and research.

## Project Structure

```
.
├── .env                    # Environment variables configuration
├── .gitignore             # Git ignore file
├── README.md              # Project documentation
├── requirements.txt       # Python dependencies
├── 1_simple_groq_agent.py # Basic Groq LLM integration
├── 2_finance_agent.py     # Single agent for financial analysis
└── 3_agent_teams.py       # Multi-agent system with research capabilities
```

## Features

### 1. Simple Groq Agent (`1_simple_groq_agent.py`)
- Basic integration with Groq's LLM
- Demonstrates fundamental agent setup
- Simple question-answering capabilities
- Uses the llama-3.3-70b-versatile model

### 2. Finance Agent (`2_finance_agent.py`)
- Stock market data analysis using YFinance
- Company symbol lookup functionality
- Displays data in formatted tables
- Provides:
  - Current stock prices
  - Fundamental data
  - Analyst recommendations

### 3. Agent Teams (`3_agent_teams.py`)
- Multi-agent system combining:
  - Research Agent: Web searches using DuckDuckGo
  - Finance Agent: Market analysis using YFinance
- Comprehensive company analysis including:
  - Latest news and developments
  - Market trends
  - Financial metrics
  - Stock analysis

## Dependencies

```
phidata>=2.7.5         # Core framework for AI agents
python-dotenv>=1.0.1   # Environment variable management
groq>=0.13.1          # Alternative LLM provider
yfinance>=0.2.51      # Financial data API
openai>=1.58.1        # OpenAI API integration
duckduckgo-search>=4.5.0  # Web search capabilities
```

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key
   GROQ_API_KEY=your_groq_api_key
   ```

## Usage

### Simple Groq Agent
```python
python 1_simple_groq_agent.py
```
This demonstrates basic interaction with the Groq LLM model.

### Finance Agent
```python
python 2_finance_agent.py
```
This will run a financial analysis for specified companies, displaying stock prices, fundamentals, and analyst recommendations.

### Agent Teams
```python
python 3_agent_teams.py
```
This will perform a comprehensive analysis using both agents:
- Research Agent: Gathers latest news and market trends
- Finance Agent: Analyzes financial metrics and stock performance

## Features

### Company Symbol Lookup
The finance agent includes a built-in company symbol lookup function supporting major companies:
- Tesla (TSLA)
- Apple (AAPL)
- Microsoft (MSFT)
- Amazon (AMZN)
- Google (GOOGL)
- And more...

### Data Presentation
- Formatted tables for financial data
- Markdown formatting for readability
- Clear separation of research and financial analysis
- Source attribution for web searches

## Security

- API keys are stored in `.env` file
- `.gitignore` configured to exclude sensitive files
- Environment variable management for secure key handling

## Attribution

This project is inspired by and builds upon examples from:
https://github.com/codebasics/ai-agents