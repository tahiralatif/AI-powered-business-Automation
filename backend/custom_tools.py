import os , requests
from dotenv import load_dotenv

load_dotenv()

Web_Search_API= os.getenv("WEB_SEARCH_API")
Search_Engine_ID= os.getenv("Search_Engine_ID")



def web_search(query: str, max_results: int = 5) -> str:
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": Web_Search_API,
        "cx": Search_Engine_ID,
        "q": query,
        "num": max_results
    }

    try:
        res= requests.get(url, params= params, timeout= 10)
        res.raise_for_status()
        data = res.json()

        if "items" not in data:
            return "No results found."
        
        lines = []

        for i, item in enumerate(data["items"], 1):
            title = item.get("title", "No title")
            link = item.get("link", "No link")
            snippet = item.get("snippet", "")
            lines.append(f"{i}. {title}\n  {link}\n  {snippet}\n")

            return "\n\n".join(lines)
        
    except Exception as e:
        return f"An error occurred during web search: {e}"
    

GNEWS_API_KEY= os.getenv("GNEWS_API_KEY")

def search_news(query:str, lang: str= "en", max_results: int=5) -> str:
    """
    Search the latest news articles using GNews API.

    Args:
        query (str): Search keyword.
        lang (str): Language code (default "en").
        max_results (int): Number of articles to return.

    Returns:
        list: List of dictionaries containing title, description, url, source, published date.
    """

    url = f"https://gnews.io/api/v4/search?q={query}&lang={lang}&max={max_results}&apikey={GNEWS_API_KEY}"
    response = requests.get(url)

    if response.status_code != 200:
        return f"Error: Unable to fetch news articles. Status code {response.status_code}"
    
    data = response.json()

    articles = []

    for article in data.get("articles", []):
        articles.append({
            "title": article.get("title"),
            "description": article.get("description"),
            "url": article.get("url"),
            "source": article.get("source", {}).get("name"),
            "publishedAt": article.get("publishedAt")
        })
    return articles