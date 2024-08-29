import mailsphinx.sphinx

import argparse
import datetime
import pytz

# Arguments for mailsphinx.py
parser = argparse.ArgumentParser()
parser.add_argument('-sm', '--send-email', action='store_true', help='If active, attempts to send emails.')
parser.add_argument('-hm', '--historical-mode', action='store_true', help='If True, downloads historical GOES data for selected period.')
parser.add_argument('-sd', '--start-datetime', type=str, default=None, help='Specifies first day of evaluation period (YYYY-MM-DD).')
parser.add_argument('-ed', '--end-datetime', type=str, default=None, help='Specifies last day of the evaluation period (YYYY-MM-DD).')
parser.add_argument('-b', '--batch', action='store_true', default=False, help='If True, runs in batch mode. Expects a --batch-directory argument.')
parser.add_argument('-bd', '--batch-directory', type=str, default=None, help='Directory that contains many *.tgz files for MailSPHINX processing.')
parser.add_argument('-bfp', '--batch-filename-pattern-startswith', type=str, default=None, help='Filters out files in batch_directory with names that do not match the provided starting pattern.')
args = parser.parse_args()





print("WARNING: If you are not on the NASA network, you will not be able to run MailSPHINX. Turn on VPN if you're offsite!")
if args.batch:
    # Batch mode
    assert(args.batch_directory is not None), '--batch-directory argument is REQUIRED for batch mode.'
    mailsphinx.sphinx.batch(args.batch_directory, args.batch_filename_pattern_startswith)
else:
    # Main program
    # CONVERT ARGS
    args.start_datetime = datetime.datetime.strptime(args.start_datetime, '%Y-%m-%d').replace(tzinfo=pytz.UTC)
    args.end_datetime = datetime.datetime.strptime(args.end_datetime, '%Y-%m-%d').replace(tzinfo=pytz.UTC)
    mailsphinx.sphinx.main(args.send_email, args.historical_mode, args.start_datetime, args.end_datetime)





