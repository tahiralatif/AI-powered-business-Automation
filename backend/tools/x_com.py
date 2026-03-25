import requests
from agents import function_tool
import os
from dotenv import load_dotenv

load_dotenv()

BEARER_TOKEN = os.getenv("BEARER_TOKEN")

@function_tool
def search_tweets(query: str, max_results: int = 5) -> list:
    """
    Search recent tweets using Twitter API v2 (read-only).
    
    Args:
        query (str): Search keyword
        max_results (int): Number of tweets (max 100)

    Returns:
        list: List of tweets with text, author_id, and id
    """
    url = "https://api.twitter.com/2/tweets/search/recent"
    headers = {"Authorization": f"Bearer {BEARER_TOKEN}"}
    params = {"query": query, "max_results": max_results, "tweet.fields": "author_id"}

    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        return [{"error": f"Failed to fetch: {response.status_code}", "detail": response.json()}]

    tweets = []
    for t in response.json().get("data", []):
        tweets.append({
            "id": t["id"],
            "author_id": t["author_id"],
            "text": t["text"],
            "url": f"https://twitter.com/i/web/status/{t['id']}"
        })
    return tweets
