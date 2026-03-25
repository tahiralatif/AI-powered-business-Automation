from agents import function_tool
import os , requests
from dotenv import load_dotenv
from custom_tools import web_search, search_news

load_dotenv()



# -------------------------------
# Market Research Backend
# -------------------------------
def _market_research(business_idea: str, target_market: str = "", competitors: str = "") -> dict:
    """
    Backend market research function using web search + news data.
    """
    insights = {}

    # Market Trends
    market_query = f"{target_market} {business_idea} market size and growth" if target_market else f"{business_idea} market trends"
    insights["market_trends"] = web_search(market_query, max_results=3)

    # Competitor Research
    if competitors:
        comp_query = f"{competitors} competitors {business_idea}"
        insights["competitor_analysis"] = web_search(comp_query, max_results=3)
    else:
        insights["competitor_analysis"] = "No specific competitors provided."

    # Latest News
    news = search_news(query=business_idea, lang="en", max_results=3)  # <-- FIXED
    insights["latest_news"] = news

    # Customer Demand Insights
    demand_query = f"customer demand {business_idea} {target_market}"
    insights["customer_demand"] = web_search(demand_query, max_results=3)

    return insights

# -------------------------------
# Market Research Tool
# -------------------------------
@function_tool
def market_research_tool(business_idea: str, target_market: str = "", competitors: str = "") -> dict:
    """
    Market Research Tool for Business Plan Agent.
    Combines market trends, competitors, news & demand analysis.
    """
    data = _market_research(business_idea, target_market, competitors)

    return {
        "business_idea": business_idea,
        "target_market": target_market if target_market else "General",
        "competitors": competitors if competitors else "Not specified",
        "research_summary": {
            "Market Trends": data["market_trends"],
            "Competitor Analysis": data["competitor_analysis"],
            "Latest News": data["latest_news"],
            "Customer Demand": data["customer_demand"],
        }
    }