from agents import function_tool
from tools.gnews_tool import search_news
import os , requests
from dotenv import load_dotenv
from custom_tools import web_search, search_news

load_dotenv()        


@function_tool
def swot_tool(business_idea: str, target_market: str = "", competitors: str = "") -> dict:
    """
    Dynamic SWOT analysis generator using web search + news data.
    """

    # Fetch market trends
    market_data = web_search(f"{target_market} {business_idea} market trends") if target_market else ""
    competitor_data = web_search(f"{competitors} competitors analysis") if competitors else ""
    news_data = search_news(query=business_idea, lang="en", max_results=3)

    strengths = [
        f"Unique positioning with idea: {business_idea}",
        "Ability to adopt AI/automation for efficiency",
        "First-mover advantage in niche" if target_market else "Can scale into multiple industries"
    ]

    weaknesses = [
        "Low funding and limited brand recognition",
        "Small team dependency",
        "Need for customer education about AI tools"
    ]

    opportunities = [
        f"Market trends show growth: {market_data}" if market_data else "Emerging market with growth potential",
        f"Recent news highlights opportunities: {news_data}" if news_data else "Positive industry signals from AI adoption",
    ]

    threats = [
        f"Strong competitors: {competitor_data}" if competitor_data else "Well-funded competitors in similar space",
        "Changing regulations in AI/data privacy",
        "Rapid technological changes"
    ]

    return {
        "business_idea": business_idea,
        "swot_analysis": {
            "Strengths": strengths,
            "Weaknesses": weaknesses,
            "Opportunities": opportunities,
            "Threats": threats,
        }
    }
