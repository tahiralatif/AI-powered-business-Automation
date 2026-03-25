
import os
import asyncio
from dotenv import load_dotenv

from agents import Agent, OpenAIChatCompletionsModel, RunConfig, AsyncOpenAI, Runner, ModelSettings, InputGuardrailTripwireTriggered, OutputGuardrailTripwireTriggered
from agent_hooks import AgentBasedHooks
from agents import RunContextWrapper, TResponseInputItem, GuardrailFunctionOutput, input_guardrail, output_guardrail
from tools.tools import web_search
from tools.gnews_tool import search_news
from tools.arxiv import search_arxiv 
from tools.reddit import get_reddit_trending
from tools.x_com import search_tweets
from tools.finance_tool import finance_tool
from tools.swot_tool import swot_tool
from tools.market_research_tool import market_research_tool
from handoffagents.bussiness_plan_agen import agent as business_plan_agent 
from handoffagents.competitorWebsiteScraper import competitorWebsiteScrapert
from handoffagents.pitch_deck_agent import pitch_deck_agent
from handoffagents.idea_generator import idea_generator_agent
from guadrails.input_guardrail import input_guard_agent
from guadrails.output_guardrails import out_guard_agent

# Load environment variables
load_dotenv()



async def main():
        
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    MODEL_NAME = "gemini-2.0-flash"

    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY environment variable not set.")

    client = AsyncOpenAI(
        api_key=GEMINI_API_KEY,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )

    Gemini_model = OpenAIChatCompletionsModel(
        model=MODEL_NAME,
        openai_client=client
    )

    config = RunConfig(
        model=Gemini_model,
        model_provider=client,
        tracing_disabled=True
    )

    # --- Input Guardrail Function ---
    @input_guardrail
    async def guardrail_input_func(
        ctx: RunContextWrapper[None],
        agent: Agent,
        input: str | list[TResponseInputItem],
    ) -> GuardrailFunctionOutput:
        result = await Runner.run(
            input_guard_agent,
            input=input,
            context=ctx.context, 
            run_config=config
        )

        return GuardrailFunctionOutput(
            output_info=result.final_output,
            tripwire_triggered=not result.final_output.is_business_or_startup_idea_competitor_pitch_related,
        )

    # Output Guardrail Function
    @output_guardrail 
    async def guardrail_output_func(
            ctx: RunContextWrapper[None],
            agent: Agent,
            input: str | list[TResponseInputItem],
        ) -> GuardrailFunctionOutput:
            result = await Runner.run(
                out_guard_agent,
                input=input,
                context=ctx.context, 
                run_config=config
            )

            return GuardrailFunctionOutput(
                output_info=result.final_output,
                tripwire_triggered=not result.final_output.is_business_or_startup_idea_competitor_pitch_related,
            )

    # -------------------------- Define the Orchestrator Agent ------------------------------------------
    triage_agent = Agent(
        name="Orchestrator Agent",
        instructions="""
        You are the Orchestrator Agent.
        Your job is to analyze the user's request and ALWAYS hand it off to the most suitable specialized agent.
        You must not solve tasks directly yourself — only route them to the right agent.
        """,
        tools=[business_plan_agent.as_tool(
            tool_name="business_plan_agent",
            tool_description="Creates structured, investor-ready business plans."
        ),
        idea_generator_agent.as_tool(
            tool_name="idea_generator_agent",
            tool_description="Generates unique, practical, and creative ideas based on user prompts."
        ),
        competitorWebsiteScrapert.as_tool(
            tool_name="competitor_website_scraper_agent",
            tool_description="Scrapes competitor websites to gather insights and data for market analysis."
        ),
        pitch_deck_agent.as_tool(
            tool_name="pitch_deck_generator_agent",
            tool_description="Generates a full 10-slide pitch deck draft."
        )
        ],
        hooks=AgentBasedHooks(),
        model_settings=ModelSettings(
            tool_choice="required",  
            max_tokens=600,
            temperature=0.9,
            top_p=0.9,
        ),
        handoffs=[business_plan_agent, idea_generator_agent, competitorWebsiteScrapert, pitch_deck_agent],
        handoff_description="""
        The Orchestrator Agent MUST select one of the following agents for every request:
        - Business Plan Agent → For structured, investor-ready business plans.
        - Idea Generator Agent → For unique, practical, and creative ideas.
        - Competitor Website Scraper Agent → For scraping and analyzing competitor websites.
        - Pitch Deck Generator Agent → For professional 10-slide pitch deck drafts.
        """,
        input_guardrails=[guardrail_input_func],
        output_guardrails=[guardrail_output_func]  
    )

    
    try:
        result = await Runner.run(
            competitorWebsiteScrapert,
            input="https://github.com/panaversity/learn-agentic-ai/tree/main/01_ai_agents_first",
            run_config=config
        )
        print(result.final_output)
        
                
    except InputGuardrailTripwireTriggered as e:
        print("invalind input")
        
        
    except OutputGuardrailTripwireTriggered as e:
       print("invalid ouput")
        
    except Exception as e:
        print("")
        



if __name__ == "__main__":
    asyncio.run(main())
    