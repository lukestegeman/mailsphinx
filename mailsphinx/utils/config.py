# Configuration file
import datetime
import pytz
import os

# Email configuration
class Email:
    def __init__(self):
        self.send_from = 'luke.a.stegeman@nasa.gov'
        self.reply_to = 'luke.a.stegeman@nasa.gov'
        self.server = 'ndc-relay.ndc.nasa.gov'
email = Email()

class Path:
    def __init__(self):
        self.report = os.path.abspath('./filesystem/public/viewable/')
        self.dataframe = os.path.abspath('./dataframes/')
        self.plot = os.path.abspath('../sphinxval/output/plots/')
        self.email_header_template = os.path.abspath('./template/email_header.html')
        self.email_image = os.path.abspath('./email_images/')
path = Path()

class Time:
    def __init__(self):
        self.week_first_day = 'Monday'
        self.week_last_day = 'Monday'
        self.weekday_index = {'Monday' : 0,
                              'Tuesday' : 1,
                              'Wednesday' : 2,
                              'Thursday' : 3,
                              'Friday' : 4,
                              'Saturday' : 5,
                              'Sunday' : 6,
                             }
        self.iswa_format_swap = datetime.datetime(year=2023, month=5, day=23)
        self.iswa_minimum_time = datetime.datetime(year=2010, month=4, day=14, hour=0, minute=0, second=0, tzinfo=pytz.UTC)
        self.hours_per_week = 168.0
time = Time()

class Color:
    def __init__(self):
        self.associations = {'Hits'                  : '#2e7d32',
                             'Correct Negatives'     : '#0b3d91',
                             'Misses'                : '#c62828',
                             'False Alarms'          : '#f57f17',
                             'Neutral'               : '#0e1111',
                             'Long X-Ray Flux'       : '#ffa500',
                             'Short X-Ray Flux'      : '#5400a8',
                             '>=1 MeV Proton Flux'   : '#b3b3b3',
                             '>=5 MeV Proton Flux'   : '#ffd480',
                             '>=10 MeV Proton Flux'  : '#ff0000',
                             '>=30 MeV Proton Flux'  : '#6b3d9a',
                             '>=50 MeV Proton Flux'  : '#0000ff',
                             '>=60 MeV Proton Flux'  : '#000000',
                             '>=100 MeV Proton Flux' : '#00ff00',
                             '>=500 MeV Proton Flux' : '#f39c12',
                             'Probability Color Main': '#7814e3',
                             'Probability Color Sub' : '#c90eb7',
                             'Divider'               : '#d92906'
                            }
        self.color_cycle = ['#d62728',  # Red
                            '#1f77b4',  # Blue
                            '#ff7f0e',  # Orange
                            '#2ca02c',  # Green
                            '#9467bd',  # Purple
                            '#8c564b',  # Brown
                            '#e377c2',  # Pink
                            '#7f7f7f',  # Gray
                            '#bcbd22',  # Yellow-Green
                            '#17becf',  # Cyan
                            '#393b79',  # Dark Blue
                            '#f7b6d2',  # Light Pink
                            '#c5b0d5',  # Light Purple
                            '#c49c94',  # Light Brown
                            '#e7ba52',  # Gold
                            '#ff9896',  # Light Red
                            '#8c6d31',  # Dark Brown
                            '#6b6ecf',  # Light Indigo
                            '#d6dbd0',  # Light Gray
                            '#bcbd22',  # Olive Green
                            '#2ca02c'   # Dark Green
                           ]
color = Color()

class Image:
    def __init__(self):
        self.dpi = 600
image = Image()

class Plot:
    def __init__(self):
        self.font = 'Arial'
        self.fontsize = 16
plot = Plot()

class Value:
    def __init__(self):
        self.minimum_log = 1e-10
value = Value()

class Html:
    def __init__(self):
        self.indent = '    '
html = Html()

# Website configuration
google_script_url = 'https://script.google.com/macros/s/AKfycbw69r0XJSpISEFmE8X8Sb2_BKQIZOmBNaU8bzcAy0GwvNfvscFwmd0UH6AsxSVnxTg-/exec'
