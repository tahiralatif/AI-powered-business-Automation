from agents import Agent, ModelSettings
from agent_hooks import AgentBasedHooks
from tools.report_export import export_report
from tools.report_export import visualize_data
from tools.report_export import export_pitchdeck

# Simple GPT-only Pitch Deck Generator Agent
pitch_deck_agent = Agent(
    name="Pitch Deck Generator Agent",
    instructions="""
    You are a Pitch Deck Generator Agent.
    Your task is to take the refined startup idea and generate a full 10-slide pitch deck draft.
    Include slide headings + bullet points:
    1. Business Name
    2. Problem Statement
    3. Solution / Product
    4. Market Opportunity
    5. Revenue Model
    6. Competition / Differentiation
    7. Go-To-Market Strategy
    8. Team / Founders
    9. Financial Projections
    10. Funding Ask
    Make it practical, concise, and persuasive.
    """,
    tools=[export_report, visualize_data, export_pitchdeck],  
    hooks=AgentBasedHooks(),
    model_settings=ModelSettings(
        tool_choice="required",
        max_tokens=1500,
        temperature=0.7
    )
)
