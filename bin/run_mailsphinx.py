import mailsphinx.mailsphinx

import argparse
import datetime
import pytz

# Arguments for mailsphinx.py
parser = argparse.ArgumentParser()
parser.add_argument('-sm', '--send-email', action='store_true', default=False, help='If active, attempts to send emails.')
parser.add_argument('-hm', '--historical-mode', action='store_true', default=False, help='If active, downloads historical GOES/ACE-EPAM data for selected period.')
parser.add_argument('-sd', '--start-datetime', type=str, default=None, help='Specifies first day of evaluation period (YYYY-MM-DD).')
parser.add_argument('-ed', '--end-datetime', type=str, default=None, help='Specifies last day of the evaluation period (YYYY-MM-DD).')
parser.add_argument('-df', '--dataframe-filename', type=str, default=None, help='Specifies dataframe to use for evaluation.')
parser.add_argument('-hmsd', '--historical-mode-save-directory', type=str, default='historical', help='Directory to which historical MailSPHINX emails are saved.')
parser.add_argument('-b', '--batch', action='store_true', default=False, help='If active, runs in batch mode. Expects a --batch-directory argument.')
parser.add_argument('-bd', '--batch-directory', type=str, default=None, help='Directory that contains many *.tgz files for MailSPHINX processing.')
parser.add_argument('-bfp', '--batch-filename-pattern-startswith', type=str, default=None, help='Filters out files in batch_directory with names that do not match the provided starting pattern.')
args = parser.parse_args()

print("WARNING: If you are not on the NASA network, you will not be able to run MailSPHINX. Turn on VPN if you're offsite!")
if args.batch:
    # Batch mode
    assert(args.batch_directory is not None), '--batch-directory argument is REQUIRED for batch mode.'
    mailsphinx.mailsphinx.batch(directory=args.batch_directory, file_pattern_startswith=args.batch_filename_pattern_startswith, historical_mode_save_directory=args.historical_mode_save_directory)
else:
    # Main program
    # CONVERT ARGS
    if (args.start_datetime is not None):
        args.start_datetime = datetime.datetime.strptime(args.start_datetime, '%Y-%m-%d').replace(tzinfo=pytz.UTC)
    if (args.end_datetime is not None):
        args.end_datetime = datetime.datetime.strptime(args.end_datetime, '%Y-%m-%d').replace(tzinfo=pytz.UTC)
    mailsphinx.mailsphinx.main(do_send_email=args.send_email, start_datetime=args.start_datetime, end_datetime=args.end_datetime, dataframe_filename=args.dataframe_filename, historical_mode_save_directory=args.historical_mode_save_directory, )

