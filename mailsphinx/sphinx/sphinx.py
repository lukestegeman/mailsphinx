# Internal modules
from ..utils import send_email
from ..utils import subscription
from ..utils import config as cfg
from ..utils import scoreboard_call

# External modules (included with Python)
import os
import zipfile
import datetime


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
        attachment = 'zips/sphinx-weekly-reports.zip'
        with zipfile.ZipFile(attachment, 'w') as z:
            for report in reports_to_compress:
                print(report)
                _, tail = os.path.split(report)
                z.write(report, arcname=tail)
        print('Reports have been compressed into ', attachment)

        text = "Take a look at this week's SPHINX report(s)! [test; do not reply]\n\n"
        text += "Models you're subscribed to:\n"
        for model in subscriber.models:
            text += model + '\n'
        
        time_of_generation = str(datetime.datetime.now())
        gen_time_dmy = time_of_generation.rsplit(' ')[0]
        gen_time_hms = time_of_generation.rsplit(' ')[1].rsplit('.')[0]
        prob_sb_url = scoreboard_call.scoreboard_call(subscriber.models, time_of_generation, 'Probability')
        int_sb_url = scoreboard_call.scoreboard_call(subscriber.models, time_of_generation, 'Intensity')

        text += '\n\n\nReady-made links to the CCMC SEP Scoreboard over the reporting period\n'
        text += 'Probablility: ' + prob_sb_url
        text += '\nIntensity: ' + int_sb_url
        text += '\nThis report was generated at ' + time_of_generation
        
        send_email.send_email('MailSPHINX: Weekly Report [test]', text, subscriber.email, attachment, send=do_send_email)

    



if __name__ == '__main__':
    None 

