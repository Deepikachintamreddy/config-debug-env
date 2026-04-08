## 📈 AI Investment Agent

### 🎓 FREE Step-by-Step Tutorial 
**👉 [Click here to follow our complete step-by-step tutorial](https://www.theunwindai.com/p/build-ai-investment-agent-with-gpt-4o) and learn how to build this from scratch with detailed code walkthroughs, explanations, and best practices.**

This AI-powered investment agent is built with Agno's AgentOS framework that analyzes stocks and generates detailed investment reports. By using GPT-5.2 with Yahoo Finance data, this app provides valuable insights to help you make informed investment decisions.

### Features
- Compare the performance of two stocks
- Retrieve comprehensive company information
- Get the latest company news and analyst recommendations
- Beautiful web UI powered by AgentOS

### How to get Started?

1. Clone the GitHub repository

```bash
git clone https://github.com/Shubhamsaboo/awesome-llm-apps.git
cd advanced_ai_agents/single_agent_apps/ai_investment_agent
```
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```
3. Get your OpenAI API Key

- Sign up for an [OpenAI account](https://platform.openai.com/) and obtain your API key.
- Export your API key:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

4. Run the AgentOS App
```bash
python investment_agent.py
```

5. Open your web browser and navigate to the URL provided in the console output to interact with the AI investment agent through the playground interface.

6. Connecting Your AgentOS

To manage, monitor, and interact with your financial agent through the AgentOS Control Plane (from your browser), you need to connect your running AgentOS instance:

**Step-by-step guide:**

- Visit the official documentation: [Connecting Your OS](https://docs.agno.com/agent-os/connecting-your-os)
- Follow the steps in the guide to register your local AgentOS and establish the connection.

### 🎯 AI INVESTMENT AGENT - OUTPUT

✅ SERVER STATUS: ACTIVE
   URL: http://localhost:7777

📊 AGENT CONFIGURATION

Agent ID: ai-investment-agent
Model: GPT-5.2-2025-12-11
Framework: Agno AgentOS
Debug Mode: ENABLED

🔧 REGISTERED TOOLS (Yahoo Finance)

✓ get_current_stock_price
✓ get_company_info
✓ get_stock_fundamentals
✓ get_income_statements
✓ get_key_financial_ratios
✓ get_analyst_recommendations
✓ get_company_news
✓ get_technical_indicators
✓ get_historical_stock_prices

🚀 HOW TO GET RESULTS

OPTION 1 - Interactive Web Interface (RECOMMENDED):
   1. Open your browser
   2. Go to: http://localhost:7777
   3. Type investment questions like:
      • "What is Apple's current stock price?"
      • "Compare Tesla and Ford stocks"
      • "Is Microsoft a good investment?"
      • "Get latest news about Amazon"

OPTION 2 - API Request (Programmatic):
   Can make HTTP requests to the running server

📝 SERVER LOGS

✓ Uvicorn running on http://localhost:7777
✓ Auto-reload enabled (watches for code changes)
✓ Application startup complete
✓ Ready to handle requests