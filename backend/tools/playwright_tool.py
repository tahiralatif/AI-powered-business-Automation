from agents import function_tool
from playwright.async_api import async_playwright
import asyncio

@function_tool
async def playwright_tool(url: str) -> dict:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url)
        content = await page.content()
        await browser.close()
    return {"tool": "Playwright", "content": content}
