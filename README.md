# MailSPHINX
Emails SPHINX reports to subscribers. Partner code of SPHINX validation code for solar energetic particle models.

This SPHINX code is not associated with sphinx-doc, the automated documentation building code.

SPHINX is developed via community challenges through the SHINE, ISWAT, ESWW, and SEPVAL conferences and in support of the SEP Scoreboards.

## Prerequisites

`Python >= 3.10.5`

## Installation

Download MailSPHINX from Github to your desired location (for convenience, assume `$mailsphinx` represents this location on your machine):
    `git clone https://github.com/lukestegeman/mailsphinx.git`

Install the required Python dependencies via `pip` (consider using a [virtual environment](https://docs.python.org/3/library/venv.html)):
    `pip install -r requirements.txt`

If you are working on a Windows machine, you must add the `$mailsphinx` directory to your `PYTHONPATH` environment variable. There are several equivalent methods to edit your `PYTHONPATH`. They are linked [here](https://www.tutorialspoint.com/how-to-set-python-environment-variable-pythonpath-on-windows).

### Checking your Installation

MailSPHINX is packaged with an example SPHINX dataframe, `$mailsphinx/example/dataframe.pkl`.

From the `$mailsphinx` directory, execute `python bin/sphinx.py`. If your installation is correct, the program should execute with no errors (warnings are expected) and a new file `$mailsphinx/filesystem/public/viewable/mailsphinx_*.html`, where the `*` is a representation of the current UTC date and time in `_YYYY-MM-DD_HHMM` format.

### Command Line Options

    `-h, --help` : Shows a help message.
    `-sm, --send-email` : If active, attempts to send emails to subscribers listed in `$mailsphinx/no_share/subscribers.csv`.
    `-df, --dataframe-filename` : Specifies the SPHINX dataframe to be parsed by MailSPHINX.
    `-hm, --historical-mode` : If active, downloads historical GOES/ACE-EPAM data for evaluation period and filters dataframe to include only forecasts issued within selected period between `start_datetime` and `end_datetime`, inclusive.
    `-hmsd, --historical-mode-save-directory` : Directory to which historical MailSPHINX emails are saved. Default is `$mailsphinx/filesystem/public/viewable/historical`.
    `-sd, --start-datetime` : Specifies first day of evaluation period (YYYY-MM-DD). If `None`, defaults to UTC Monday prior to most recent UTC Monday. Time fixed at 00:00 UTC.
    `-ed, --end-datetime` : Specifies last day of the evaluation period (YYYY-MM-DD). If `None`, defaults to most recent UTC Monday (including today, if it is UTC Monday). Time fixed at 00:00 UTC.
    `-b, --batch` : If active, runs in batch mode, which will generate many MailSPHINX HTML files. Does not allow for email distribution. Expects a --batch-directory argument.
    `-bd, --batch-directory` : Directory that contains many `*.tgz` files for MailSPHINX processing.
    `-bfp, --batch-filename-pattern-startswith` : Filters out files in `batch_directory` with names that do not match the provided starting pattern.

### Configuration Settings

Configuration settings are dictated by the `$mailsphinx/mailsphinx/utils/config.py` file. Here, the user can customize most tunable aspects of MailSPHINX emails, such as colors, plot settings, etc. Families of settings are organized into very simple C++struct-like classes (e.g., `Email` and `Path`).

The `Email` class specifies the email address and server from which MailSPHINX emails are sent:
    
    **`Email.send_from` : Email from which to send MailSPHINX emails.**
    **`Email.reply_to` : Email to which MailSPHINX email recipients will reply to.**
    **`Email.server` : Server that ultimately sends a bunch of emails.**

All three of these fields should be modified.

Most importantly, the user is able to modify paths to important locations for retrieving data and storing MailSPHINX-generated content within the `Path` class. The purpose of each path is listed below:

    `Path.filesystem` : Directory where MailSPHINX-generated content is archived.
    `Path.report` : Directory where SPHINX reports are archived (subdirectory of `Path.filesystem`).
    `Path.other` : Directory where intermediate data is archived (subdirectory of `Path.filesystem`).
    `Path.email_storage` : Directory where MailSPHINX emails are stored as HTML files (subdirectory of `Path.filesystem`).
    `Path.index` : `index.html` file location; an HTML file for navigating the MailSPHINX Archive.
    `Path.index_stylesheet` : `styles.css` file location; the CSS stylesheet for the MailSPHINX Archive.
    `Path.example` : Directory where files used in MailSPHINX example execution are stored.
    `Path.template` : Directory where HTML template files are stored.
    `Path.email_image` : Directory where images for MailSPHINX emails and HTML files are temporarily stored.
    `Path.email_header_template` : Template HTML file that contains header information for MailSPHINX emails.
    `Path.index_template` : Template HTML file that contains header information for MailSPHINX Archive.
    `Path.index_template_stylesheet` : Template CSS stylesheet file for MailSPHINX Archive.
    `Path.all_time_statistics_overview` : Data file that contains all-time forecast statistics since last reset.

    **`Path.external_report_location` : Directory where SPHINX-generated validation reports are stored; this path is used for their retrieval and inclusion into the MailSPHINX Archive.**
    **`Path.subscriber_data` : Data file that contains a list of email addresses for those who have subscribed to MailSPHINX.**

The three paths in **bold** will need to be modified by the user. 

### Specifying `Path.dataframe`

This path should point to the location where SPHINX will routinely generate/update the all-time SPHINX dataframe pickle file (`*.pkl`). This can be alternatively specified at the command line using the `--dataframe-filename` argument.

### Specifying `Path.external_report_location`

This path should point to the location where SPHINX will routinely generate/update HTML (`*.html`) and Markdown (`*.md`) reports. This can be an absolute path or a relative path from the `$mailsphinx` directory.

### Adding Subscribers

The user **must** create a list of subscribers in a directory specified by `Path.subscriber_data` in order to send emails. For privacy reasons, it is preferable that this directory is not tracked by `git`. The default directory is `$mailsphinx/no_share`, but this must be created by the user directly, as must the list of subscriber email addresses, `$mailsphinx/no_share/subscribers.csv`.

From the `$mailsphinx` directory, make a new directory called `no_share` (e.g., `mkdir no_share`).

From within the `$mailsphinx/no_share` directory, make a new file named `subscribers.csv`. This file should have the following structure, where `person.*@example.com` represents a generic email address of a MailSPHINX subscriber:

```
email
person.a@example.com
person.b@example.com
person.c@example.com
```
