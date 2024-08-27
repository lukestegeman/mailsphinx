# Internal modules
from ..utils import send_email
from ..utils import subscription
from ..utils import build_text
from ..utils import config
from ..utils import format_objects

# External modules (included with Python)
import datetime
import glob
import os
import shutil

def main(do_send_email=False, historical=False, start_datetime=None, end_datetime=None):
    """
    Main MailSPHINX function.
        Compiles HTML reports, 
        compiles subscribers,
        and sends SPHINX reports to subscribers via email.

    Parameters
    ----------
    do_send_email : bool
    
    historical : bool
    
    start_datetime : NoneType, datetime

    end_datetime : NoneType, datetime 
    """

    # RESET IMAGES
    if os.path.exists(config.path.email_image):
        print('deleting...')
        shutil.rmtree(config.path.email_image)
    if not os.path.exists(config.path.email_image):
        os.mkdir(config.path.email_image)

    # COLLECT HTML REPORTS AND STORE IN FILESYSTEM
    html_files = glob.glob(os.path.join(config.path.external_report_location, '*.html'))
    for f in html_files:
        shutil.copy(f, os.path.join(config.path.report, os.path.basename(f))) 

    # GENERATE EMAIL CONTENT
    if ((start_datetime is None) or (end_datetime is None)) and historical:
        historical = False
        print('Missing start_datetime or end_datetime; setting historical = False.') 
    html = build_text.build_text(is_historical=historical, convert_images_to_base64=False, start_datetime=start_datetime, end_datetime=end_datetime)
    
    # SAVE IN FILESYSTEM
    savefile = os.path.join(config.path.email_storage, 'mailsphinx_' + config.time.generation_time.replace(' ', '_').replace(':', '') + '.html')
    html_webpage_text = format_objects.convert_cids_to_image_paths(html)

    a = open(savefile, 'w')
    a.write(html_webpage_text)
    a.close()

    # COLLECT SUBSCRIBERS
    subscribers = subscription.load_subscribers()

    # SEND EMAIL TO ALL RECIPIENTS
    if do_send_email:
        for subscriber in subscribers:
            send_email.send_email('MailSPHINX: Weekly Report [test]', html, subscriber.email, send=do_send_email)



if __name__ == '__main__':
    None 

