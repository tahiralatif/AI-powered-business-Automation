from agents import Agent, ModelSettings
from agent_hooks import AgentBasedHooks
from tools.finance_tool import finance_tool
from tools.swot_tool import swot_tool
from tools.market_research_tool import market_research_tool
from tools.formater_tool import formatter_tool

agent = Agent(
    name="Business Plan Agent",
    instructions="You are a Business Plan Agent. You create structured, investor-ready business plans.",
    tools=[market_research_tool, finance_tool, swot_tool],  
    hooks=AgentBasedHooks(),
    model_settings=ModelSettings(
        tool_choice="required",
        max_tokens=800,
        temperature=0.7
    ),
)
