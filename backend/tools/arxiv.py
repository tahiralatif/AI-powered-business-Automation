import feedparser
from agents import function_tool
from urllib.parse import quote

@function_tool
def search_arxiv(query: str, max_results: int = 5) -> list:
    """
    Search research papers on arXiv.

    Args:
        query (str): Search keyword.
        max_results (int): Number of papers to return (default=5).

    Returns:
        list: List of dictionaries with title, summary, published date, and URL.
    """
    # Encode query properly (space, special chars -> URL safe)
    encoded_query = quote(query)

    url = f"http://export.arxiv.org/api/query?search_query=all:{encoded_query}&start=0&max_results={max_results}"
    feed = feedparser.parse(url)

    papers = []
    for entry in feed.entries:
        papers.append({
            "title": entry.title,
            "summary": entry.summary,
            "published": entry.published,
            "url": entry.id
        })

    return papers
