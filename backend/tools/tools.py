import os , requests
from agents import function_tool 
from dotenv import load_dotenv

load_dotenv()

Web_Search_API= os.getenv("WEB_SEARCH_API")
Search_Engine_ID= os.getenv("Search_Engine_ID")


@function_tool
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

            
