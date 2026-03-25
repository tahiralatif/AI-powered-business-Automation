import requests
from agents import function_tool

@function_tool
def get_reddit_trending(subreddit: str = "popular", limit: int = 5) -> list:
    """
    Fetch trending posts from Reddit without authentication.

    Args:
        subreddit (str): Subreddit name (default 'popular')
        limit (int): Number of posts to fetch (default 5)

    Returns:
        list: List of dictionaries with title, score, subreddit, and URL
    """
    url = f"https://www.reddit.com/r/{subreddit}/top.json?limit={limit}&t=day"
    headers = {"User-Agent": "hackathon-app/0.1"}
    response = requests.get(url, headers=headers)

    posts = []
    if response.status_code == 200:
        data = response.json()
        for item in data["data"]["children"]:
            post = item["data"]
            posts.append({
                "title": post["title"],
                "score": post["score"],
                "subreddit": post["subreddit"],
                "url": f"https://reddit.com{post['permalink']}"
            })
    else:
        return [{"error": f"Failed to fetch: {response.status_code}"}]

    return posts
