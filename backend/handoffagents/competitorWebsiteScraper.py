import json
import os
from datetime import datetime
from agents import Agent, ModelSettings
from agent_hooks import AgentBasedHooks
from tools.playwright_tool import playwright_tool
from tools.Firecrawl_tool import firecrawl_tool

# Import notification tools
from integrations.slack_notifier import send_slack_alert
from integrations.email_sender import send_report_email
from integrations.google_sheets import update_competitor_sheet

BASELINE_FILE = "data/competitor_baseline.json"

def check_for_pricing_changes(competitor_name, current_price, current_features):
    """
    Compares current data with baseline and triggers alerts if changes are found.
    """
    if not os.path.exists("data"):
        os.makedirs("data")

    # Load baseline
    baseline = {}
    if os.path.exists(BASELINE_FILE):
        with open(BASELINE_FILE, "r") as f:
            baseline = json.load(f)

    old_data = baseline.get(competitor_name, {})
    old_price = old_data.get("price", "Unknown")
    
    # Check if anything changed
    if old_price != current_price:
        print(f"🚨 CHANGE DETECTED for {competitor_name}!")
        
        # 1. Update Google Sheet
        update_competitor_sheet(competitor_name, old_price, current_price)
        
        # 2. Send Slack Alert
        msg = f"*Price Change Detected!*\n• Competitor: {competitor_name}\n• Old Price: {old_price}\n• New Price: {current_price}\n• Features: {current_features}"
        send_slack_alert(msg)
        
        # 3. Update baseline
        baseline[competitor_name] = {
            "price": current_price,
            "features": current_features,
            "last_checked": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        with open(BASELINE_FILE, "w") as f:
            json.dump(baseline, f, indent=4)
            
        return True
    
    return False

competitorWebsiteScrapert = Agent(
    name=" Competitor Website Scraper Agent",
    instructions="""
    You are a Competitor Website Scraper Agent. 
    You scrape competitor websites to gather insights and data for market analysis.
    If you detect pricing information, you must call the internal price change detection logic.
    """,
    tools=[playwright_tool, firecrawl_tool],  
    hooks=AgentBasedHooks(),
    model_settings=ModelSettings(
        tool_choice="required",
        max_tokens=400,
        temperature=0.7
    ),
)
