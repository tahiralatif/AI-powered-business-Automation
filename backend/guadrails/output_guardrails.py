from pydantic import BaseModel
from agents import Agent

# --- OUTPUT SCHEMA ---
class OutputSchema(BaseModel):
    is_business_or_startup_idea_competitor_pitch_related: bool
    reasoning: str
    refined_idea: str
    answer: str
    message: str  # for clear error/debug messages


# --- Guardrail Agent ---
out_guard_agent = Agent(
    name="Output Guardrail Agent",
    instructions="""
    You are an Output Guardrail Agent.
    You ensure that the model’s output is relevant to business ideas, startups, competitor analysis, or pitch decks.
    If the output is irrelevant:
    - Set `is_business_or_startup_idea_competitor_pitch_related` to false
    - Explain why in `reasoning`
    - Leave `refined_idea` empty
    - Add a short user-facing explanation in `message`
    """,
    output_type=OutputSchema,
)
