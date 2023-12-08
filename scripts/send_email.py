import smtplib
import os
import sys
import logging
from email.mime.text import MIMEText
from dotenv import load_dotenv

launcher_path = sys.argv[1]

logger = logging.getLogger("send_email_logger")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(f"{launcher_path}/temp/send_email.log")
logger.addHandler(handler)
handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s", "%Y-%m-%d %H:%M:%S"))


load_dotenv()
smpt_host = os.environ['SMPT_HOST']
smpt_port = os.environ['SMPT_PORT']
smpt_user = os.environ['SMPT_USER']
smpt_pass = os.environ['SMPT_PASS']
receiver_email = os.environ['RECEIVER_EMAIL']
sender_email = os.environ['SENDER_EMAIL']


def send_email(subject, message, sender_email, receiver_email, smtp_server, smtp_port, smtp_username, smtp_password, attachment=None):
    msg = MIMEText(message)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = receiver_email

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            if attachment:
                msg.attach(attachment)
            server.sendmail(sender_email, receiver_email, msg.as_string())
            print("Email sent successfully")
    except Exception as e:
        print(f"Failed to send email: {e}")


with open(f'{launcher_path}/logs/job_error.log', 'r') as log_file:
    log_content = log_file.read()

    email_subject = "Job Failed"
    email_message = f"This is an alert that job failed a number of times.\n\nLog contents:\n{log_content}"

send_email(
    subject=email_subject,
    message=email_message,
    sender_email=f"{sender_email}",
    receiver_email=f"{receiver_email}",
    smtp_server=f"{smpt_host}",
    smtp_port=f"{smpt_port}",
    smtp_username=f"{smpt_user}",
    smtp_password=f"{smpt_pass}"
    )
