# Configuration file
import datetime
import os
import pytz

from ..utils import build_color

# Email configuration
class Email:
    def __init__(self):
        self.send_from = 'luke.a.stegeman@nasa.gov'
        self.reply_to = 'luke.a.stegeman@nasa.gov'
        self.server = 'ndc-relay.ndc.nasa.gov'
email = Email()

class Path:
    def __init__(self):
        self.filesystem = os.path.abspath(os.path.join('filesystem', 'public', 'viewable'))
        self.report = os.path.abspath(os.path.join(self.filesystem, 'report'))
        self.other = os.path.abspath(os.path.join(self.filesystem, 'other'))
        self.all_time_statistics_overview = os.path.abspath(os.path.join(self.other, 'all_time_statistics_overview.pkl'))
        self.email_storage = os.path.abspath(os.path.join(self.filesystem, 'email'))
        self.index = os.path.abspath(os.path.join(self.filesystem, 'index.html'))
        self.index_stylesheet = os.path.abspath(os.path.join(self.filesystem, 'styles.css'))
        self.example = os.path.abspath('example')
        self.template = os.path.abspath('template')
        self.email_image = os.path.abspath('email_images')
        self.email_header_template = os.path.abspath(os.path.join(self.template, 'email_header.html'))
        self.index_template = os.path.abspath(os.path.join(self.template, 'index_header.html'))
        self.index_template_stylesheet = os.path.abspath(os.path.join(self.template, 'styles.css'))
        # MOST LIKELY TO REQUIRE USER INTERVENTION
        self.dataframe = os.path.abspath(os.path.join(self.example, 'dataframe.pkl'))
        self.external_report_location = os.path.abspath(os.path.join(self.example, 'reports'))
        self.subscriber_data = os.path.abspath(os.path.join('no_share', 'subscribers.csv'))
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
        self.generation_time = None
time = Time()

class Relabel:
    def __init__(self):
        self.event_summary = {'Energy': 'Energy',
                              'Flux Threshold': 'Flux Threshold',
                              'Observatory' : 'Observatory', 
                              'Observed SEP Threshold Crossing Time' : 'Threshold Crossing Time',
                              'Observed SEP End Time' : 'End Time',
                              'Observed SEP Duration' : 'Duration',
                              'Observed SEP Fluence' : 'Fluence',
                              'Observed SEP Peak Intensity (Onset Peak)' : 'Onset Peak Flux',
                              'Observed SEP Peak Intensity (Onset Peak) Time' : 'Onset Peak Time',
                              'Observed SEP Peak Intensity Max (Max Flux)' : 'Max Flux',
                              'Observed SEP Peak Intensity Max (Max Flux) Time' : 'Max Flux Time'
                             }
relabel = Relabel()

class Plot:
    def __init__(self):
        self.font = 'Arial'
        self.fontsize = 16
        self.marker_size = 100
        self.opacity = 0.3
plot = Plot()

class Color:
    def __init__(self):
        self.associations = {'Hits'                    : '#2e7d32',
                             'Correct Negatives'       : '#0b3d91',
                             'Misses'                  : '#c62828',
                             'False Alarms'            : '#f57f17',
                             'Neutral'                 : '#0e1111',
                             'Not Evaluated'           : '#000000',
                             'Long X-Ray Flux'         : '#ffa500',
                             'Short X-Ray Flux'        : '#5400a8',
                             '>=1 MeV Proton Flux'     : '#b3b3b3',
                             '>=5 MeV Proton Flux'     : '#ffd480',
                             '>=10 MeV Proton Flux'    : '#ff0000',
                             '>=30 MeV Proton Flux'    : '#6b3d9a',
                             '>=50 MeV Proton Flux'    : '#0000ff',
                             '>=60 MeV Proton Flux'    : '#000000',
                             '>=100 MeV Proton Flux'   : '#00ff00',
                             '>=500 MeV Proton Flux'   : '#f39c12',
                             '38-53 keV Electron Flux' : '#808080',
                             '175-315 keV Electron Flux' : '#00faff',
                             'Probability Color Main'  : '#7814e3',
                             'Probability Color Sub'   : '#c90eb7',
                             'Divider'                 : '#d92906',
                             'Eruption Out of Range'   : '#000000',
                             'Trigger/Input after Observed Phenomenon' : '#000000',
                             'No Matching Threshold' : '#000000',
                             'Ongoing SEP Event' : '#000000',
                             'Unmatched' : '#000000',
                             'No Prediction Provided' : '#000000',
                             None: 'none'
                             }
        self.associations['&ge; 1'] = self.associations['>=1 MeV Proton Flux']
        self.associations['&ge; 5'] = self.associations['>=5 MeV Proton Flux']
        self.associations['&ge; 10'] = self.associations['>=10 MeV Proton Flux']
        self.associations['&ge; 30'] = self.associations['>=30 MeV Proton Flux']
        self.associations['&ge; 50'] = self.associations['>=50 MeV Proton Flux']
        self.associations['&ge; 60'] = self.associations['>=60 MeV Proton Flux']
        self.associations['&ge; 100'] = self.associations['>=100 MeV Proton Flux']
        self.associations['&ge; 500'] = self.associations['>=500 MeV Proton Flux']
       
        self.associations['>=10 MeV, >=10 pfu Event'] = build_color.get_transparent_color(self.associations['>=10 MeV Proton Flux'], plot.opacity)
        self.associations['>=30 MeV, >=1 pfu Event'] = build_color.get_transparent_color(self.associations['>=30 MeV Proton Flux'], plot.opacity)
        self.associations['>=50 MeV, >=1 pfu Event'] = build_color.get_transparent_color(self.associations['>=50 MeV Proton Flux'], plot.opacity)
        self.associations['>=100 MeV, >=1 pfu Event'] = build_color.get_transparent_color(self.associations['>=100 MeV Proton Flux'], plot.opacity)
 
        self.color_cycle = ['#000000',  # Black
                            '#17becf',  # Cyan
                            '#7f7f7f',  # Gray
                            '#bcbd22',  # Yellow-Green
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
                            '#2ca02c',  # Dark Green
                            '#9467bd',  # Purple
                            '#8c564b',  # Brown
                            '#e377c2',  # Pink
                           ]
        self.legend_background = '#ffffff'
color = Color()

class Shape:
    def __init__(self):
        self.associations = {'Neutral' : 'o',
                             'Hits' : 'o',
                             'Misses' : 'o',
                             'False Alarms' : 'o',
                             'Correct Negatives' : 'o',
                             'SEP Event' : 'o',
                             'No SEP Event' : 's',
                             'Eruption Out of Range' : 'X',
                             'Trigger/Input after Observed Phenomenon': 'd',
                             'No Matching Threshold' : '*', 
                             'Ongoing SEP Event' : '>',
                             'Unmatched' : '2',
                             'No Prediction Provided' : '+',
                             None : 'None'}
        self.contingency = 'o'
        self.left_arrow = '<'
        self.right_arrow = '>'
shape = Shape()

class Image:
    def __init__(self):
        self.dpi = 72
        self.width = 12
        self.height = 6
        self.height_contingency = 3
        self.peak_flux_width = 8 
        self.peak_flux_height = 6
        self.cid_dict = {}
        self.cid_dict_index = 0
        self.width_legend = 6
        self.height_legend = 3
        self.advanced_warning_base_height = 1.0
        self.vertical_category_allotment_advanced_warning = 0.25
image = Image()

class Index:
    def __init__(self):
        self.contingency = {'Hits' : 4,
                            'Misses' : 3,
                            'False Alarms' : 2,
                            'Correct Negatives' : 1,
                            'Not Evaluated' : 0
                           }
index = Index()

class Value:
    def __init__(self):
        self.minimum_log = 1e-10
value = Value()

class Html:
    def __init__(self):
        self.indent = '    '
        self.max_width = '1000px'
        self.probability_width_percentage = 115
        self.left_padding_fraction = 0.2
        self.template_variables = {'body_padding' : '100px'}
html = Html()

class Type:
    def __init__(self):
        self.dataframe = {'Model' : str,
                          'Energy Channel Key' : str,
                          'Threshold Key' : str,
                          'Mismatch Allowed' : bool,
                          'Prediction Energy Channel Key' : str,
                          'Prediction Threshold Key' : str,
                          'Forecast Source' : str,
                          'Forecast Path' : str,
                          'Forecast Issue Time' : datetime.datetime,
                          'Prediction Window Start' : datetime.datetime,
                          'Prediction Window End' : datetime.datetime,
                          'Number of CMEs' : int,
                          'CME Start Time' : datetime.datetime,
                          'CME Liftoff Time' : datetime.datetime,
                          'CME Latitude' : float,
                          'CME Longitude' : float,
                          'CME Speed' : float,
                          'CME Half Width' : float,
                          'CME PA' : float,
                          'CME Catalog' : str,
                          'Number of Flares' : int,
                          'Flare Latitude' : float,
                          'Flare Longitude' : float,
                          'Flare Start Time' : datetime.datetime,
                          'Flare Peak Time' : datetime.datetime,
                          'Flare End Time' : datetime.datetime,
                          'Flare Last Data Time' : datetime.datetime,
                          'Flare Intensity' : float,
                          'Flare Integrated Intensity' : float,
                          'Flare NOAA AR' : int,
                          'Observatory' : str,
                          'Observed Time Profile' : str,
                          'Observed SEP All Clear' : bool,
                          'Observed SEP Probability' : int,
                          'Observed SEP Threshold Crossing Time' : datetime.datetime,
                          'Observed SEP Start Time' : datetime.datetime,
                          'Observed SEP End Time' : datetime.datetime,
                          'Observed SEP Duration' : float,
                          'Observed SEP Fluence' : float,
                          'Observed SEP Fluence Units' : str,
                          'Observed SEP Fluence Spectrum' : list,
                          'Observed SEP Peak Intensity (Onset Peak)' : float,
                          'Observed SEP Peak Intensity (Onset Peak) Units' : str,
                          'Observed SEP Peak Intensity (Onset Peak) Time' : datetime.datetime,
                          'Observed SEP Peak Intensity Max (Max Flux)' : float,
                          'Observed SEP Peak Intensity Max (Max Flux) Units' : str,
                          'Observed SEP Peak Intensity Max (Max Flux) Time' : datetime.datetime,
                          'Observed Point Intensity' : float,
                          'Observed Point Intensity Units' : str,
                          'Observed Point Intensity Time' : datetime.datetime,
                          'Observed Max Flux in Prediction Window' : float,
                          'Observed Max Flux in Prediction Window Units' : str,
                          'Observed Max Flux in Prediction Window Time' : str,
                          'Predicted SEP All Clear' : bool,
                          'All Clear Match Status' : str,
                          'Predicted SEP Probability' : float,
                          'Probability Match Status' : str,
                          'Predicted SEP Threshold Crossing Time' : datetime.datetime,
                          'Threshold Crossing Time Match Status' : str,
                          'Predicted SEP Start Time' : datetime.datetime,
                          'Start Time Match Status' : str,
                          'Predicted SEP End Time' : datetime.datetime,
                          'End Time Match Status' : str,
                          'Predicted SEP Duration' : float,
                          'Duration Match Status' : str,
                          'Predicted SEP Fluence' : float,
                          'Predicted SEP Fluence Units' : str,
                          'Fluence Match Status' : str,
                          'Predicted SEP Fluence Spectrum' : list,
                          'Predicted SEP Fluence Spectrum Units' : str,
                          'Fluence Spectrum Match Status' : str,
                          'Predicted SEP Peak Intensity (Onset Peak)' : float,
                          'Predicted SEP Peak Intensity (Onset Peak) Units' : str,
                          'Predicted SEP Peak Intensity (Onset Peak) Time' : datetime.datetime,
                          'Peak Intensity Match Status' : str,
                          'Predicted SEP Peak Intensity Max (Max Flux)' : float,
                          'Predicted SEP Peak Intensity Max (Max Flux) Units' : str,
                          'Predicted SEP Peak Intensity Max (Max Flux) Time' : datetime.datetime,
                          'Peak Intensity Max Match Status' : str,
                          'Predicted Point Intensity' : float,
                          'Predicted Point Intensity Units' : str,
                          'Predicted Point Intensity Time' : datetime.datetime,
                          'Predicted Time Profile' : str,
                          'Time Profile Match Status' : str,
                          'Last Data Time to Issue Time' : float  
                          }
type = Type()

class Order:
    def __init__(self):
        self.energy_order = [1, 5, 10, 30, 50, 60, 100, 500]
        self.energy_key_order = ['min.1.0.max.-1.0.units.MeV',
                                 'min.5.0.max.-1.0.units.MeV',
                                 'min.10.0.max.-1.0.units.MeV',
                                 'min.30.0.max.-1.0.units.MeV',
                                 'min.50.0.max.-1.0.units.MeV',
                                 'min.60.0.max.-1.0.units.MeV',
                                 'min.100.0.max.-1.0.units.MeV',
                                 'min.500.0.max.-1.0.units.MeV'
                                ]
order = Order()

# CAREFUL WITH THESE
reset_all_time_df = False

