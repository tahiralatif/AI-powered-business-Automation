import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv

load_dotenv()

def send_report_email(report_path: str, recipient_email: str, summary: str = "Your AI Co-founder has generated a new report."):
    """
    Sends an email with the report attached.
    """
    sender_email = os.getenv("EMAIL_USER")
    sender_password = os.getenv("EMAIL_PASSWORD")

    if not sender_email or not sender_password:
        print("⚠️ Email credentials not found in .env. Skipping email.")
        return

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = "🚀 AI Co-founder: Your Feasibility Report is Ready"

    body = f"Hello,\n\n{summary}\n\nPlease find the attached report for full details.\n\nBest regards,\nYour AI Co-founder"
    msg.attach(MIMEText(body, 'plain'))

    # Attachment
    filename = os.path.basename(report_path)
    try:
        with open(report_path, "rb") as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f"attachment; filename= {filename}")
            msg.attach(part)

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        print(f"📧 Email sent successfully to {recipient_email}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
