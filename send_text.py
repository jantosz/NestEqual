import ssl
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from os import getenv


load_dotenv()
GMAIL_USER = getenv('GMAIL_ACC')
GMAIL_PASS = getenv('GMAIL_PASS')


def send(phone_num, provider_email, subject, message_text):
    receiver_email = phone_num + provider_email

    message = MIMEMultipart()
    message['From'] = GMAIL_USER
    message['To'] = receiver_email
    message['Subject'] = subject

    message.attach(MIMEText('\n' + message_text + '  ', 'plain'))

    text = message.as_string()

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as server:
        server.login(GMAIL_USER, GMAIL_PASS)
        server.sendmail(GMAIL_USER, receiver_email, text)