# Internal modules
from ..utils import build_text
from ..utils import config
from ..utils import format_objects
from ..utils import manipulate_dates
from ..utils import send_email
from ..utils import setup_directory_structure
from ..utils import subscription

# External modules (included with Python)
import calendar
import datetime
import glob
import os
import pytz
import shutil
import tarfile

def main(do_send_email=False, start_datetime=None, end_datetime=None, convert_images_to_base64=False, dataframe_filename=None, save_directory_sub='', external_report_location=None):
    """
    Main MailSPHINX function.
        Compiles HTML reports, 
        compiles subscribers,
        and sends SPHINX reports to subscribers via email.

    Parameters
    ----------
    do_send_email : bool
    
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
    if external_report_location is None:
        external_report_location = config.path.external_report_location
    path = os.path.join(external_report_location, '*.html')
    html_files = glob.glob(path)
    for f in html_files:
        shutil.copy(f, os.path.join(config.path.report, os.path.basename(f))) 

    if (start_datetime is None) and (end_datetime is None):
        # ASSUME THE MOST RECENT WEEK PERIOD
        start_datetime, end_datetime = manipulate_dates.get_mailsphinx_boundaries(config.time.week_first_day, config.time.week_last_day)
    elif ((start_datetime is None) and (end_datetime is not None)):
        # THROW AN ERROR
        assert(), 'Please supply an --end-datetime.'        
    elif ((start_datetime is not None) and (end_datetime is None)):
        # THROW AN ERROR
        assert(), 'Please supply a --start-datetime.'

    # start_datetime AND end_datetime ARE KNOWN
   
    # GENERATE EMAIL CONTENT 
    html = build_text.build_text(start_datetime=start_datetime, end_datetime=end_datetime, convert_images_to_base64=convert_images_to_base64, dataframe_filename=dataframe_filename)
    
    # SAVE IN FILESYSTEM
    save_directory = os.path.join(config.path.email_storage, save_directory_sub)
    if not os.path.exists(save_directory):
        os.mkdir(save_directory)
    savefile = os.path.join(save_directory, 'mailsphinx_' + start_datetime.strftime('%Y-%m-%dT%H:%M:%S').replace(' ', '_').replace(':', '') + '_' + end_datetime.strftime('%Y-%m-%dT%H:%M:%S').replace(' ', '_').replace(':', '') + '.html')

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
            send_email.send_email('MailSPHINX Test: ISEP (Internal) Email List', html, subscriber.email, send=do_send_email)
    
def batch(directory, file_pattern_startswith=None, save_directory_sub='batch'):
    """
    Batch mode for generating many HTML files. Mainly for testing.
    
    Parameters
    ----------
    directory : str
    """
    dataframe_path = './.tmp/SPHINX_dataframe.pkl'    

    # READ DIRECTORY
    zip_files = os.listdir(directory)
    
    if file_pattern_startswith is not None:
        zip_files = [file for file in zip_files if file.startswith(file_pattern_startswith)]
    zip_files.sort()
    
    if os.path.exists('./.tmp'):
        shutil.rmtree('./.tmp')
    os.mkdir('./.tmp')
    os.mkdir('./.tmp/reports')
    # LOOP THROUGH FILES
    for file in zip_files:
        time_tag = file.split('_')[-1].rstrip('.tgz')
        tarfile_path = os.path.join(time_tag, 'output', 'pkl', 'SPHINX_dataframe.pkl')
        tarfile_report_path = os.path.join(time_tag, 'reports')
        # EXTRACT ONLY THE SPHINX DATAFRAME
        with tarfile.open(os.path.join(directory, file), 'r:gz') as tar:
            for member in tar.getmembers():
                if member.name.replace('/', '\\') == tarfile_path:
                    extracted_file = tar.extractfile(member)
                    with open(dataframe_path, 'wb') as f:
                        f.write(extracted_file.read())
                    break
        with tarfile.open(os.path.join(directory, file), 'r:gz') as tar:
            report_directory = []
            for member in tar.getmembers():
                if member.name.replace('/', '\\').startswith(tarfile_report_path) and member.isfile():
                    member.name = os.path.basename(member.name)
                    tar.extract(member, path='./.tmp/reports/')
            
        year = int(time_tag[:4])
        month = int(time_tag[4:])
        days_in_month = calendar.monthrange(year, month)[1]
        start_datetime = datetime.datetime(year=year, month=month, day=1).replace(tzinfo=pytz.UTC)
        end_datetime = datetime.datetime(year=year, month=month, day=days_in_month).replace(tzinfo=pytz.UTC)
        main(do_send_email=False, start_datetime=start_datetime, end_datetime=end_datetime, convert_images_to_base64=True, dataframe_filename=dataframe_path, save_directory_sub=save_directory_sub, external_report_location='./.tmp/reports/')
        
if __name__ == '__main__':
    None 

