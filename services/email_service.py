import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import streamlit as st
import os

def send_email(to_email: str, subject: str, body: str, attachment_path: str = None):
    """
    Sends an email. For MVP, we will simulate this by logging to console
    if no SMTP secrets are configured.
    """
    if not to_email:
        print(f"[Email] Skipped: No recipient.")
        return False

    smtp_config = st.secrets.get("smtp")
    
    # If no SMTP config, mock it
    if not smtp_config:
        print(f"--- [MOCK EMAIL] ---")
        print(f"To: {to_email}")
        print(f"Subject: {subject}")
        print(f"Body: {body}")
        if attachment_path:
            print(f"Attachment: {attachment_path}")
        print(f"--------------------")
        return True

    try:
        msg = MIMEMultipart()
        msg['From'] = smtp_config.get("sender_email", "noreply@trek.com.br")
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        if attachment_path and os.path.exists(attachment_path):
            with open(attachment_path, "rb") as f:
                part = MIMEApplication(f.read(), Name=os.path.basename(attachment_path))
            part['Content-Disposition'] = f'attachment; filename="{os.path.basename(attachment_path)}"'
            msg.attach(part)

        server = smtplib.SMTP(smtp_config["server"], smtp_config["port"])
        server.starttls()
        server.login(smtp_config["username"], smtp_config["password"])
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"[Email] Error: {e}")
        return False
