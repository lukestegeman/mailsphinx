# Internal modules
from ..utils import send_email
from ..utils import subscription
from ..utils import build_text
from ..utils import config


# External modules (included with Python)
import os
import datetime

'''
def main(report_path, do_send_email=False):
    """
    Main MailSPHINX function.
        Compiles HTML reports, 
        compiles subscribers and their preferences,
        and sends SPHINX reports to subscribers via email.

    Parameters
    ----------
    report_path : path, from top-level mailsphinx/ directory, to folder containing reports. 
    """

    # Collect the reports
    if report_path[-1] != os.sep:
        report_path += os.sep
    reports_ = os.listdir(report_path)
    reports = [report_path + file for file in reports_ if not file.endswith('.md')]

    # Read the recipient list and apply their appropriate subscription options
    subscribers = subscription.load_subscribers()
    
    # Attach to email and send to recipient list
    for subscriber in subscribers:
        print(subscriber.name, subscriber.email, subscriber.models)

        # Find the reports this subscriber wants
        reports_to_compress = []
        for model in subscriber.models:
            model_filename = report_path + model + '_report.html'
            if model_filename in reports:
                reports_to_compress.append(model_filename)

        # Apply compression
        #attachment = 'zips/sphinx-weekly-reports.zip'
        #with zipfile.ZipFile(attachment, 'w') as z:
        #    for report in reports_to_compress:
        #        print(report)
        #        _, tail = os.path.split(report)
        #        z.write(report, arcname=tail)
        #print('Reports have been compressed into ', attachment)

        attachment = None        

        text = build_text.build_text(subscriber)
        
        send_email.send_email('MailSPHINX: Weekly Report [test]', text, subscriber.email, attachment, send=do_send_email)
'''

def main(do_send_email=False, historical=False):
    """
    """

    # GENERATE EMAIL CONTENT
    html = build_text.build_text(historical=historical, convert_images_to_base64=True)
    
    # SEND EMAIL TO ALL RECIPIENTS
    #if do_send_email:
    #    send_email.send_email('MailSPHINX: Weekly Report [test]', html, ...)
        
    
     
    

    



if __name__ == '__main__':
    None 

