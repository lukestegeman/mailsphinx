import mailsphinx.sphinx
import argparse

# Arguments for mailsphinx.py
parser = argparse.ArgumentParser()

parser.add_argument('-rep', '--report-path', type=str, default='./reports/', help='Path, from top-level mailsphinx/ directory, to folder containing reports.')

parser.add_argument('-tm', '--test-email', action='store_true', help='If active, does not attempt to send emails.')

args = parser.parse_args()

# Main program)
mailsphinx.sphinx.main(args.report_path, args.test_email)
print("WARNING: If you are not on the NASA network, you will not be able to run MailSPHINX. Turn on VPN if you're offsite!")
print("WARNING: You'll need the Google Sheets API JSON key to run MailSPHINX. Ask for it if you need it.")

