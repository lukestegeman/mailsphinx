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
args = parser.parse_args()

# CONVERT ARGS
args.start_datetime = datetime.datetime.strptime(args.start_datetime, '%Y-%m-%d').replace(tzinfo=pytz.UTC)
args.end_datetime = datetime.datetime.strptime(args.end_datetime, '%Y-%m-%d').replace(tzinfo=pytz.UTC)

# Main program
mailsphinx.sphinx.main(args.send_email, args.historical_mode, args.start_datetime, args.end_datetime)
print("WARNING: If you are not on the NASA network, you will not be able to run MailSPHINX. Turn on VPN if you're offsite!")
print("WARNING: You'll need the Google Sheets API JSON key to run MailSPHINX. Ask for it if you need it.")



