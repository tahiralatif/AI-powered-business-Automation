
import os
import requests
from agents import function_tool

FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")

@function_tool(is_enabled= True)
def firecrawl_tool(url: str) -> dict:
    endpoint = "https://api.firecrawl.dev/v1/crawl"
    headers = {"Authorization": f"Bearer {FIRECRAWL_API_KEY}"}
    payload = {"url": url, "extract": ["text", "links"]}
    res = requests.post(endpoint, headers=headers, json=payload)
    data = res.json()
    html_text = " ".join(data.get("text", []))
    return {"tool": "Firecrawl", "content": html_text}