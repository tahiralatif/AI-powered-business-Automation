from pydantic import BaseModel
from agents import (
    input_guardrail,
    Agent,
    
)

# --- OUTPUT SCHEMA ---
class OutputSchema(BaseModel):
    is_business_or_startup_idea_competitor_pitch_related: bool
    reasoning: str
    refined_idea: str
    answer: str


# --- Guardrail Agent ---
input_guard_agent = Agent(
    name="Input Guardrail Agent",
    instructions="""
    You are an Input Guardrail Agent.
    You ensure that user inputs are relevant to business ideas, startups, or pitch decks.
    If the input is irrelevant, mark it as not related.
    """,
    output_type=OutputSchema,
)



