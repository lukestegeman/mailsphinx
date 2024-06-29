import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.utils import COMMASPACE, formatdate
from email import encoders
from pathlib import Path
import os

from ..utils import config as cfg




def send_email(subject, body, recipient, attachment=None, send=False):
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

    # Attach files
    if attachment is not None:
        part.set_payload(open(attachment, 'rb').read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="' + os.path.basename(attachment) + '"')
        message.attach(part)

    # Configure email
    message['From'] = cfg.email.send_from
    message['To'] = recipient
    message['Subject'] = subject 
    message['reply-to'] = cfg.email.reply_to

    # Attach text
    message.attach(MIMEText(body))

    # Set up email client
    smtp = smtplib.SMTP(cfg.email.server)
    
    # Sending email
    if send:
        print('Sending email to the following address: ', recipient)
        smtp.sendmail(cfg.email.send_from, recipient, message.as_string())
    else:
        print('Pretending to send email to the following address: ', recipient)

    # Close the email client
    smtp.close()


if __name__ == '__main__':
   pass 
    
    






