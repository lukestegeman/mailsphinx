from ..utils import config

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.utils import COMMASPACE, formatdate
from email import encoders

import os
import pandas as pd
import smtplib

def send_email(subject, body, recipient, send=False):
    """
    Creates an email with an arbitrary number of recipients and attachments.

    Parameters
    ----------
    subject : string
        Email subject line.

    body : string
        Email body text.

    recipient : string
        Email address.

    attachments : list of string
        Optional. List of attachments to send.

    send : bool
        Optional. If True, sends email. If False, bypasses send command (for testing).
    
    Returns
    -------
    None
    """
    
    message = MIMEMultipart()
    part = MIMEBase('application', 'octet-stream')

    # Configure email
    message['From'] = config.email.send_from
    message['To'] = recipient
    message['Subject'] = subject 
    message['reply-to'] = config.email.reply_to

    # Attach text
    message.attach(MIMEText(body, 'html'))

    # Attach images
    for path, cid in config.image.cid_dict.items():
        with open(path, 'rb') as image_file:
            image = MIMEImage(image_file.read())
            image.add_header('Content-ID', '<' + cid + '>')
            message.attach(image)

    # Set up email client
    smtp = smtplib.SMTP(config.email.server)
    
    # Sending email
    if send:
        print('Sending email to the following address: ', recipient)
        smtp.sendmail(config.email.send_from, recipient, message.as_string())
    else:
        print('Pretending to send email to the following address: ', recipient)

    # Close the email client
    smtp.close()


if __name__ == '__main__':
   pass 
    
    






