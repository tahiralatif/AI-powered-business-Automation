import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv

load_dotenv()

def send_report_email(report_path: str, recipient_email: str, summary: str = "Your AI Co-founder has generated a new business report."):
    """
    Sends a professional HTML email with the report attached.
    """
    sender_email = os.getenv("EMAIL_USER")
    sender_password = os.getenv("EMAIL_PASSWORD")

    if not sender_email or not sender_password:
        print("⚠️ Email credentials not found in .env. Skipping email.")
        return

    msg = MIMEMultipart()
    msg['From'] = f"AI Co-founder Automation <{sender_email}>"
    msg['To'] = recipient_email
    msg['Subject'] = "🚀 Business Insight: Your Feasibility Report is Ready"

    # --- PROFESSIONAL HTML TEMPLATE ---
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

    # Attach HTML body
    msg.attach(MIMEText(html_content, 'html'))

    # --- ATTACHMENT ---
    filename = os.path.basename(report_path)
    try:
        with open(report_path, "rb") as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f"attachment; filename= {filename}")
            msg.attach(part)

        # SMTP Connection
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        print(f"📧 Professional HTML Email sent successfully to {recipient_email}")
    except Exception as e:
        print(f"❌ Failed to send professional email: {e}")
