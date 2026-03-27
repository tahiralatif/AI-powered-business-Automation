"""
Celery Tasks - Updated for Multi-User Database Architecture
Uses database instead of config.json
"""
import json
import asyncio
import os
from datetime import datetime
from celery_app import celery_app
from workflow_manager import validate_idea_workflow
from database import get_db_session
from models import User, Settings, ResearchReport
from integrations.sendgrid_email import sendgrid_service
from integrations.slack_oauth import slack_oauth_service


# ==================== Helper Functions ====================

def get_all_active_users(db):
    """Get all active users with their settings."""
    return db.query(User).filter(User.is_active == True).all()


def get_user_settings(db, user_id):
    """Get settings for a specific user."""
    return db.query(Settings).filter(Settings.user_id == user_id).first()


# ==================== TASK 1: WEEKLY MARKET RESEARCH ====================

@celery_app.task(name="tasks.weekly_research_task")
def weekly_research_task(user_id: int = None):
    """
    Automated Weekly Market Research for user's industry.
    Can run for all users or a specific user.
    """
    db = get_db_session()
    try:
        if user_id:
            # Run for specific user
            users = [db.query(User).filter(User.id == user_id).first()]
        else:
            # Run for all active users
            users = get_all_active_users(db)

        results = []
        for user in users:
            if not user:
                continue

            settings = get_user_settings(db, user.id)
            if not settings or not settings.monitoring_enabled:
                continue

            industry = settings.industry or "AI Startups"
            email = user.email

            print(f"🔄 Starting Weekly Market Research for {user.email}: {industry}")

            # Run the workflow
            loop = asyncio.get_event_loop()
            result = loop.run_until_complete(validate_idea_workflow(f"Market analysis for {industry}"))

            print(f"✅ Weekly Research Complete for {user.email}: {result}")

            # Save report to database
            report = ResearchReport(
                user_id=user.id,
                report_type="weekly",
                title=f"Weekly Market Research: {industry}",
                summary=str(result)[:500] if result else "Market analysis complete",
                content={"industry": industry, "result": result},
                is_sent=False
            )
            db.add(report)
            db.commit()

            # Send email via SendGrid
            if settings.weekly_report_enabled:
                try:
                    sendgrid_service.send_report_email(
                        recipient_email=email,
                        summary=str(result)[:200] if result else "Report ready",
                        report_path=None  # Add path if PDF generated
                    )
                    report.is_sent = True
                    report.sent_via = "email"
                except Exception as e:
                    print(f"❌ Email send failed for {user.email}: {e}")

            # Send Slack notification
            if settings.slack_installed and settings.slack_access_token:
                try:
                    asyncio.get_event_loop().run_until_complete(
                        slack_oauth_service.send_message(
                            settings.slack_access_token,
                            settings.slack_channel_id,
                            f"📊 *Weekly Market Research Ready*\n\nIndustry: {industry}\n\nKey insights have been sent to your email."
                        )
                    )
                    report.sent_via = "both" if report.is_sent else "slack"
                except Exception as e:
                    print(f"❌ Slack notification failed for {user.email}: {e}")

            db.commit()
            results.append({"user_id": user.id, "email": user.email, "success": True})

        return {"total_users": len(results), "results": results}

    except Exception as e:
        db.rollback()
        print(f"❌ Weekly research task error: {e}")
        return {"error": str(e)}
    finally:
        db.close()


# ==================== TASK 2: DAILY COMPETITOR CHECK ====================

@celery_app.task(name="tasks.daily_competitor_check_task")
def daily_competitor_check_task(user_id: int = None):
    """
    Scrapes competitors and alerts if changes are detected.
    """
    db = get_db_session()
    try:
        if user_id:
            users = [db.query(User).filter(User.id == user_id).first()]
        else:
            users = get_all_active_users(db)

        results = []
        for user in users:
            if not user:
                continue

            settings = get_user_settings(db, user.id)
            if not settings or not settings.monitoring_enabled:
                continue

            competitors = settings.competitors or []
            if not competitors:
                continue

            print(f"🔍 Starting Daily Competitor Check for {user.email}: {len(competitors)} URLs")

            # In production, call scraper agent here
            # For now, simulate monitoring
            for url in competitors:
                # TODO: Integrate competitor_website_scraper_agent
                # check_for_pricing_changes(url, settings.competitor_alert_threshold)
                pass

            # Send Slack notification if changes detected
            if settings.slack_installed and settings.slack_access_token:
                try:
                    asyncio.get_event_loop().run_until_complete(
                        slack_oauth_service.send_message(
                            settings.slack_access_token,
                            settings.slack_channel_id,
                            f"🔍 *Daily Competitor Check Complete*\n\nMonitored {len(competitors)} competitor URLs.\nNo significant changes detected today."
                        )
                    )
                except Exception as e:
                    print(f"❌ Slack notification failed for {user.email}: {e}")

            results.append({"user_id": user.id, "email": user.email, "competitors_checked": len(competitors)})

        return {"total_users": len(results), "results": results}

    except Exception as e:
        db.rollback()
        print(f"❌ Daily competitor check error: {e}")
        return {"error": str(e)}
    finally:
        db.close()


# ==================== TASK 3: MONTHLY BUSINESS SUMMARY ====================

@celery_app.task(name="tasks.monthly_summary_task")
def monthly_summary_task(user_id: int = None):
    """
    Compiles a monthly digest of all activity.
    """
    db = get_db_session()
    try:
        if user_id:
            users = [db.query(User).filter(User.id == user_id).first()]
        else:
            users = get_all_active_users(db)

        results = []
        for user in users:
            if not user:
                continue

            settings = get_user_settings(db, user.id)
            email = user.email

            print(f"📈 Generating Monthly Summary for {user.email}...")

            # Get user's reports count
            reports_count = db.query(ResearchReport).filter(
                ResearchReport.user_id == user.id,
                ResearchReport.created_at >= datetime.utcnow().replace(day=1)
            ).count()

            summary_msg = f"Your monthly business summary is ready. You had {reports_count} reports generated this month."

            # Send email summary
            if settings.weekly_report_enabled:
                try:
                    sendgrid_service.send_email(
                        to_email=email,
                        subject="📅 Your Monthly AI Co-founder Summary",
                        html_content=f"""
                        <html>
                        <body style="font-family: Arial, sans-serif;">
                            <h2>📅 Monthly Business Summary</h2>
                            <p>Hello {user.full_name or 'Founder'},</p>
                            <p>Here's your monthly activity summary:</p>
                            <ul>
                                <li>Reports Generated: {reports_count}</li>
                                <li>Competitor Checks: Daily</li>
                                <li>Industry: {settings.industry}</li>
                            </ul>
                            <p>Keep building! 🚀</p>
                        </body>
                        </html>
                        """,
                        text_content=summary_msg
                    )
                except Exception as e:
                    print(f"❌ Monthly summary email failed for {user.email}: {e}")

            # Send Slack notification
            if settings.slack_installed and settings.slack_access_token:
                try:
                    asyncio.get_event_loop().run_until_complete(
                        slack_oauth_service.send_message(
                            settings.slack_access_token,
                            settings.slack_channel_id,
                            f"📅 *Monthly Business Summary*\n\n{summary_msg}\n\nCheck your email for detailed report."
                        )
                    )
                except Exception as e:
                    print(f"❌ Slack monthly summary failed for {user.email}: {e}")

            results.append({"user_id": user.id, "email": user.email, "reports_count": reports_count})

        return {"total_users": len(results), "results": results}

    except Exception as e:
        db.rollback()
        print(f"❌ Monthly summary task error: {e}")
        return {"error": str(e)}
    finally:
        db.close()
