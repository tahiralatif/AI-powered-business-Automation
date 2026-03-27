import os
import praw
from dotenv import load_dotenv
from agents import function_tool

load_dotenv()

def get_reddit_client():
    """
    Initializes the PRAW Reddit client using environment variables.
    """
    client_id = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")
    user_agent = os.getenv("REDDIT_USER_AGENT", "AI-Co-founder:v1.0")

    if not client_id or not client_secret:
        return None

    return praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent
    )

@function_tool
def get_reddit_trending(subreddit: str = "startups", limit: int = 5) -> list:
    """
    Fetch trending/top posts from a specific subreddit using official PRAW API.

    Args:
        subreddit (str): Subreddit name (default 'startups')
        limit (int): Number of posts to fetch (default 5)

    Returns:
        list: List of dictionaries with title, score, subreddit, and URL
    """
    reddit = get_reddit_client()
    
    if not reddit:
        return [{"error": "Reddit API credentials not configured in .env"}]

    try:
        sub = reddit.subreddit(subreddit)
        posts = []
        for post in sub.top(time_filter="day", limit=limit):
            posts.append({
                "title": post.title,
                "score": post.score,
                "subreddit": post.subreddit.display_name,
                "url": f"https://reddit.com{post.permalink}"
            })
        return posts
    except Exception as e:
        return [{"error": f"Failed to fetch Reddit data: {str(e)}"}]
