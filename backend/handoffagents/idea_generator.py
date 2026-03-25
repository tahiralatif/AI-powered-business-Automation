
from agents import Agent, ModelSettings
from agent_hooks import AgentBasedHooks
from tools.tools import web_search
from tools.gnews_tool import search_news
from tools.arxiv import search_arxiv
from tools.reddit import get_reddit_trending
from tools.x_com import search_tweets


idea_generator_agent = Agent(
        name= "Idea Generator Agent",
        instructions= " You are an Idea Generator Agent. You generate unique, practical and creative ideas based on user prompts. ",
        tools= [ get_reddit_trending, search_tweets, web_search, search_news, search_arxiv],
        hooks= AgentBasedHooks(),
        model_settings= ModelSettings(tool_choice= "required", max_tokens= 600, temperature= 0.9, top_p= 0.9 ),
)