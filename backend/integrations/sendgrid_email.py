"""
SendGrid Email Service - Professional Email Delivery
Replaces Gmail SMTP for startup-scale email sending
"""
import os
import sys

# Fix Windows console encoding for emoji support
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
from dotenv import load_dotenv

load_dotenv()


class SendGridService:
    """
    Professional email service using SendGrid API.
    Benefits:
    - 100 emails/day free tier
    - Better deliverability (no spam)
    - Professional from address
    - Delivery tracking and analytics
    """

    def __init__(self):
        self.api_key = os.getenv("SENDGRID_API_KEY")
        self.from_email = os.getenv("SENDGRID_FROM_EMAIL", "noreply@yourdomain.com")
        self.from_name = os.getenv("SENDGRID_FROM_NAME", "AI Co-founder Automation")

        if not self.api_key:
            print("⚠️ SendGrid API key not found. Email delivery will be disabled.")

        self.sg = None
        if self.api_key:
            self.sg = SendGridAPIClient(self.api_key)

    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str = None,
        attachment_path: str = None
    ) -> bool:
        """
        Send a professional email using SendGrid.

        Args:
            to_email: Recipient email address
            subject: Email subject line
            html_content: HTML body content
            text_content: Plain text alternative (optional)
            attachment_path: Path to file attachment (optional)

        Returns:
            bool: True if sent successfully, False otherwise
        """
        if not self.sg:
            print("❌ SendGrid not configured. Skipping email.")
            return False

        try:
            # Create email message
            message = Mail(
                from_email=f"{self.from_name} <{self.from_email}>",
                to_emails=to_email,
                subject=subject,
                plain_text_content=text_content or subject,
                html_content=html_content
            )

            # Add attachment if provided
            if attachment_path and os.path.exists(attachment_path):
                with open(attachment_path, "rb") as f:
                    data = f.read()
                    f.close()

                    attachment = Attachment(
                        FileContent(data),
                        FileName(os.path.basename(attachment_path)),
                        FileType("application/pdf"),
                        Disposition("attachment")
                    )
                    message.attachment = attachment

            # Send email
            response = self.sg.send(message)

            if response.status_code == 202:
                print(f"📧 SendGrid email sent successfully to {to_email}")
                return True
            else:
                print(f"❌ SendGrid error: {response.status_code} - {response.body}")
                return False

        except Exception as e:
            print(f"❌ SendGrid exception: {e}")
            return False

    def send_report_email(
        self,
        recipient_email: str,
        summary: str,
        report_path: str = None
    ) -> bool:
        """
        Send a professional business report email.
        This replaces the old Gmail SMTP version.

        Args:
            recipient_email: User's email address
            summary: Brief summary of report findings
            report_path: Path to PDF report (optional)

        Returns:
            bool: Success status
        """
        subject = "🚀 Business Insight: Your Feasibility Report is Ready"

        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
            <div style="max-width: 600px; margin: auto; background-color: #ffffff; padding: 30px; border-radius: 10px; border: 1px solid #ddd;">

                <h2 style="color: #2c3e50; text-align: center;">🚀 AI Co-founder Automation</h2>

                <p style="color: #555; font-size: 16px;">Hello,</p>

                <p style="color: #555; font-size: 16px;">Your <b>Autonomous Business Intelligence Report</b> has been successfully generated.</p>

                <div style="background-color: #f9f9f9; padding: 15px; border-left: 5px solid #3498db; margin: 20px 0;">
                    <p style="color: #333; font-size: 15px; margin: 0;"><b>Summary of Findings:</b></p>
                    <p style="color: #666; font-size: 14px; margin-top: 5px;">{summary}</p>
                </div>

                <p style="color: #555; font-size: 16px;">We have attached a detailed PDF containing:
                    <ul>
                        <li>Latest Market Trends (Reddit, News)</li>
                        <li>Competitor Pricing & Analysis</li>
                        <li>SWOT Analysis & Financial Projections</li>
                    </ul>
                </p>

                <div style="text-align: center; margin-top: 30px;">
                    <a href="https://your-saas-dashboard.com" style="background-color: #3498db; color: white; padding: 12px 25px; text-decoration: none; font-weight: bold; border-radius: 5px; font-size: 16px;">
                        View Live Dashboard
                    </a>
                </div>

                <hr style="border: 0; border-top: 1px solid #eee; margin-top: 40px;">

                <p style="color: #999; font-size: 12px; text-align: center;">
                    © 2026 AI Co-founder SaaS. All rights reserved.<br>
                    You are receiving this because your automated business tracking is enabled.
                </p>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        AI Co-founder Automation - Report Ready

        Hello,

        Your Autonomous Business Intelligence Report has been successfully generated.

        Summary of Findings:
        {summary}

        The report includes:
        - Latest Market Trends (Reddit, News)
        - Competitor Pricing & Analysis
        - SWOT Analysis & Financial Projections

        © 2026 AI Co-founder SaaS. All rights reserved.
        """

        return self.send_email(
            to_email=recipient_email,
            subject=subject,
            html_content=html_content,
            text_content=text_content,
            attachment_path=report_path
        )

    def send_welcome_email(self, recipient_email: str, user_name: str = None) -> bool:
        """
        Send a welcome email to new users.

        Args:
            recipient_email: User's email address
            user_name: User's name (optional)

        Returns:
            bool: Success status
        """
        subject = "🎉 Welcome to AI Co-founder Automation!"

        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
            <div style="max-width: 600px; margin: auto; background-color: #ffffff; padding: 30px; border-radius: 10px; border: 1px solid #ddd;">

                <h2 style="color: #2c3e50; text-align: center;">🎉 Welcome to AI Co-founder!</h2>

                <p style="color: #555; font-size: 16px;">Hello {user_name or 'Founder'},</p>

                <p style="color: #555; font-size: 16px;">
                    Thank you for joining AI Co-founder Automation. We're excited to help you build your startup!
                </p>

                <div style="background-color: #f9f9f9; padding: 15px; border-left: 5px solid #27ae60; margin: 20px 0;">
                    <p style="color: #333; font-size: 15px; margin: 0;"><b>What's Next?</b></p>
                    <ul style="color: #666; font-size: 14px; margin-top: 10px;">
                        <li>Connect your Slack workspace for instant alerts</li>
                        <li>Configure your industry and competitors</li>
                        <li>Get your first AI-powered market analysis</li>
                    </ul>
                </div>

                <div style="text-align: center; margin-top: 30px;">
                    <a href="https://your-saas-dashboard.com/setup" style="background-color: #27ae60; color: white; padding: 12px 25px; text-decoration: none; font-weight: bold; border-radius: 5px; font-size: 16px;">
                        Complete Your Setup
                    </a>
                </div>

                <hr style="border: 0; border-top: 1px solid #eee; margin-top: 40px;">

                <p style="color: #999; font-size: 12px; text-align: center;">
                    © 2026 AI Co-founder SaaS. All rights reserved.
                </p>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        Welcome to AI Co-founder Automation!

        Hello {user_name or 'Founder'},

        Thank you for joining AI Co-founder Automation. We're excited to help you build your startup!

        What's Next?
        - Connect your Slack workspace for instant alerts
        - Configure your industry and competitors
        - Get your first AI-powered market analysis

        © 2026 AI Co-founder SaaS. All rights reserved.
        """

        return self.send_email(
            to_email=recipient_email,
            subject=subject,
            html_content=html_content,
            text_content=text_content
        )


# Singleton instance
sendgrid_service = SendGridService()


# Backward compatible function for existing code
def send_report_email(report_path: str, recipient_email: str, summary: str = "Your AI Co-founder has generated a new business report."):
    """
    Backward compatible function for existing task code.
    Uses SendGrid instead of Gmail SMTP.
    """
    return sendgrid_service.send_report_email(
        recipient_email=recipient_email,
        summary=summary,
        report_path=report_path
    )
