from agents import Agent, ModelSettings
from agent_hooks import AgentBasedHooks
from tools.playwright_tool import playwright_tool
from tools.Firecrawl_tool import firecrawl_tool


competitorWebsiteScrapert = Agent(
    name=" Competitor Website Scraper Agent",
    instructions=" You are a Competitor Website Scraper Agent. You scrape competitor websites to gather insights and data for market analysis.",
    tools=[playwright_tool, firecrawl_tool],  
    hooks=AgentBasedHooks(),
    model_settings=ModelSettings(
        tool_choice="required",
        max_tokens=400,
        temperature=0.7
    ),
)
