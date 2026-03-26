import os
from celery import Celery
from celery.schedules import crontab
from dotenv import load_dotenv

load_dotenv()

# Production-Style Celery Configuration
# Redis is used as both Broker (Message Queue) and Backend (Result Storage)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "ai_co_founder_tasks",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["tasks"]
)

# Optimization settings for production
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    worker_prefetch_multiplier=1, # Better for long-running scraping tasks
)

# Automated Schedules (The Heart of Business Automation)
celery_app.conf.beat_schedule = {
    # TASK 1: Weekly Market Research (Every Monday at 9 AM)
    "weekly-market-research-task": {
        "task": "tasks.weekly_research_task",
        "schedule": crontab(day_of_week=1, hour=9, minute=0),
    },
    # TASK 2: Daily Competitor Check (Every Night at 11 PM)
    "daily-competitor-check-task": {
        "task": "tasks.daily_competitor_check_task",
        "schedule": crontab(hour=23, minute=0),
    },
    # TASK 3: Monthly Business Summary (1st of every month at 8 AM)
    "monthly-summary-task": {
        "task": "tasks.monthly_summary_task",
        "schedule": crontab(day_of_month=1, hour=8, minute=0),
    },
}
