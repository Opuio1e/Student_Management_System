import smtplib, ssl
from email.message import EmailMessage

def send_email(to_address, subject, body):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = your_email
    msg['To'] = to_address
    msg.set_content(body)
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(your_email, your_password)
        smtp.send_message(msg)
