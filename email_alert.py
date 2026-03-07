import smtplib
import os
from email.mime.text import MIMEText

def send_email(failed_domains):

    sender = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASS")
    receiver = sender

    subject = "DNS Monitoring Alert"

    body = "Failed Domains:\n\n"

    for d in failed_domains:
        body += d + "\n"

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = receiver

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(sender, password)
    server.sendmail(sender, receiver, msg.as_string())
    server.quit()