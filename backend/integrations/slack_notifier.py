import requests
import os
from dotenv import load_dotenv

load_dotenv()

def send_slack_alert(message: str, channel: str = "#business-alerts"):
    """
    Sends a notification to a Slack channel using an Incoming Webhook.
    """
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    
    if not webhook_url:
        print("⚠️ Slack Webhook URL not found in .env. Skipping alert.")
        return

    payload = {
        "text": f"🔔 *AI Co-founder Alert*\n{message}",
        "channel": channel
    }

    try:
        response = requests.post(webhook_url, json=payload)
        if response.status_code == 200:
            print("💬 Slack alert sent successfully.")
        else:
            print(f"❌ Failed to send Slack alert: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Slack notification error: {e}")
