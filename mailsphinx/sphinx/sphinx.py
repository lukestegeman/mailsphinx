# Internal modules
from ..utils import send_email
from ..utils import subscription
from ..utils import build_text
from ..utils import config
from ..utils import format_objects
from ..utils import setup_directory_structure

# External modules (included with Python)
import datetime
import glob
import os
import shutil
import tarfile
import calendar
import pytz

def main(do_send_email=False, historical=False, start_datetime=None, end_datetime=None, convert_images_to_base64=False, dataframe_filename=None, historical_mode_save_directory='historical'):
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
    
    # DEFAULT TO CONFIG-SPECIFIED DATAFRAME
    if dataframe_filename is None:
        dataframe_filename = config.path.dataframe
        print('SPHINX dataframe is ', config.path.dataframe)

    # RESET IMAGES
    if os.path.exists(config.path.email_image):
        shutil.rmtree(config.path.email_image)

    # SETUP DIRECTORIES
    setup_directory_structure.make_directories()

    # COLLECT HTML REPORTS AND STORE IN FILESYSTEM
    html_files = glob.glob(os.path.join(config.path.external_report_location, '*.html'))
    for f in html_files:
        shutil.copy(f, os.path.join(config.path.report, os.path.basename(f))) 

    # GENERATE EMAIL CONTENT
    if ((start_datetime is None) or (end_datetime is None)) and historical:
        historical = False
        print('Missing start_datetime or end_datetime; setting historical = False.') 
    html = build_text.build_text(is_historical=historical, convert_images_to_base64=convert_images_to_base64, start_datetime=start_datetime, end_datetime=end_datetime, dataframe_filename=dataframe_filename)
    
    # SAVE IN FILESYSTEM
    if historical:
        save_directory = os.path.join(config.path.email_storage, historical_mode_save_directory)
        if not os.path.exists(save_directory):
            os.mkdir(save_directory)
        savefile = os.path.join(save_directory, 'mailsphinx_' + start_datetime.strftime('%Y-%m-%dT%H:%M:%S').replace(' ', '_').replace(':', '') + '_' + end_datetime.strftime('%Y-%m-%dT%H:%M:%S').replace(' ', '_').replace(':', '') + '.html')
    else:
        savefile = os.path.join(config.path.email_storage, 'mailsphinx_' + config.time.generation_time.replace(' ', '_').replace(':', '') + '.html')
    html_webpage_text = format_objects.convert_cids_to_image_paths(html)
    a = open(savefile, 'w')
    a.write(html_webpage_text)
    a.close()

    # MAKE index.html
    setup_directory_structure.make_index_html()

    # SEND EMAIL TO ALL RECIPIENTS
    if do_send_email:
        # COLLECT SUBSCRIBERS
        subscribers = subscription.load_subscribers()
        for subscriber in subscribers:
            send_email.send_email('MailSPHINX: Weekly Report [test]', html, subscriber.email, send=do_send_email)

    
def batch(directory, file_pattern_startswith=None, historical_mode_save_directory='historical'):
    """
    Batch mode for generating many HTML files. Mainly for testing.
    
    Parameters
    ----------
    directory : str
    """
    dataframe_path = './.tmp/SPHINX_dataframe.pkl'    
    config.reset_all_time_df = True
    if os.path.exists(config.path.all_time_statistics_overview):
        os.remove(config.path.all_time_statistics_overview)

    # READ DIRECTORY
    zip_files = os.listdir(directory)
    
    if file_pattern_startswith is not None:
        zip_files = [file for file in zip_files if file.startswith(file_pattern_startswith)]
    zip_files.sort()
    
    if os.path.exists('./.tmp'):
        shutil.rmtree('./.tmp')
    os.mkdir('./.tmp')
    exit_early = False
    # LOOP THROUGH FILES
    for file in zip_files:
        print(file)
        time_tag = file.split('_')[-1].rstrip('.tgz')
        if int(time_tag) < 202204:
            continue
        # EXTRACT ONLY THE SPHINX DATAFRAME
        with tarfile.open(os.path.join(directory, file), 'r:gz') as tar:
            for member in tar.getmembers():
                tarfile_path = os.path.join(time_tag, 'output', 'pkl', 'SPHINX_dataframe.pkl')
                if member.name.replace('/', '\\') == tarfile_path:
                    extracted_file = tar.extractfile(member)
                    with open(dataframe_path, 'wb') as f:
                        f.write(extracted_file.read())
                        exit_early = True
                    break
        
        config.reset_all_time_df = False

        year = int(time_tag[:4])
        month = int(time_tag[4:])
        days_in_month = calendar.monthrange(year, month)[1]
        start_datetime = datetime.datetime(year=year, month=month, day=1).replace(tzinfo=pytz.UTC)
        end_datetime = datetime.datetime(year=year, month=month, day=days_in_month).replace(tzinfo=pytz.UTC)
        main(do_send_email=False, historical=True, start_datetime=start_datetime, end_datetime=end_datetime, convert_images_to_base64=True, dataframe_filename=dataframe_path, historical_mode_save_directory=historical_mode_save_directory)
        
        if exit_early:
            print('Remove this line in mailsphinx/sphinx/sphinx.py when you would like to run in proper batch mode again.')
            exit()

if __name__ == '__main__':
    None 

