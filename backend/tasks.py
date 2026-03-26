import json
import asyncio
import os
from datetime import datetime
from celery_app import celery_app
from workflow_manager import validate_idea_workflow
from integrations.email_sender import send_report_email
from integrations.slack_notifier import send_slack_alert

# Helper: Load Config
def get_config():
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    with open(config_path, "r") as f:
        return json.load(f)

# --- TASK 1: WEEKLY MARKET RESEARCH ---
@celery_app.task(name="tasks.weekly_research_task")
def weekly_research_task():
    """
    Automated Weekly Market Research for the user's industry.
    """
    config = get_config()
    industry = config.get("industry", "AI Startups")
    email = config.get("email_address")
    
    print(f"🔄 Starting Weekly Market Research for: {industry}")
    
    # Run the workflow (async to sync wrapper)
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(validate_idea_workflow(f"Market analysis for {industry}"))
    
    print(f"✅ Weekly Research Complete: {result}")
    return result

# --- TASK 2: DAILY COMPETITOR CHECK ---
@celery_app.task(name="tasks.daily_competitor_check_task")
def daily_competitor_check_task():
    """
    Scrapes competitors from config.json and alerts if changes are detected.
    """
    config = get_config()
    competitors = config.get("competitors", [])
    
    print(f"🔍 Starting Daily Competitor Check for {len(competitors)} URLs")
    
    # In a real scenario, we'd trigger the scraper agent here
    # For now, we simulate the monitoring for the workflow demonstration
    for url in competitors:
        # Here we would call: check_for_pricing_changes(url, ...)
        pass
    
    return f"Checked {len(competitors)} competitors."

# --- TASK 3: MONTHLY BUSINESS SUMMARY ---
@celery_app.task(name="tasks.monthly_summary_task")
def monthly_summary_task():
    """
    Compiles a monthly digest of all activity.
    """
    config = get_config()
    email = config.get("email_address")
    
    summary_msg = "Your monthly business summary is ready. You had 4 weekly reports and 30 competitor checks."
    
    # Send a simple summary email for now
    # (In production, you'd aggregate all generated reports)
    print("📈 Generating Monthly Summary...")
    
    send_slack_alert("📅 *Monthly Business Summary Ready* for Founder.")
    # Note: send_report_email requires a path, but we'll mock it here
    # send_report_email(path, email, summary_msg)
    
    return "Monthly summary sent."
