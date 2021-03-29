import os
import ssl
import smtplib
from email import encoders
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate

from dotenv import load_dotenv

from modules.ticket import Ticket


def send_mail(subject, text: dict):
    if os.getcwd().endswith('modules'):
        os.chdir('..')
    path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(path):
        load_dotenv(path)
    password = os.environ.get('PASSWORD_EMAIL')
    sender_email = os.environ.get('EMAIL')

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = subject
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    msg.attach(MIMEText(text['msg-text']))

    for f in text['number_places']:
        ticket = Ticket(text['film_title'], text['hall_id'],
                        f.split('-')[0], f.split('-')[1],
                        text['time_start'], text['time_end'],
                        text['phone']).bytes_str
        part = MIMEApplication(
            ticket,
            Name=f'Билет на {text["film_title"]}-{f}.jpg'
        )
        encoders.encode_base64(part)
        part[
            'Content-Disposition'] = \
            f'attachment; filename=Билет на {text["film_title"]}-{f}.jpg'
        msg.attach(part)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, subject, msg.as_string())
