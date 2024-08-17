from ..utils import scoreboard_call
from ..utils import build_space_weather_summary
from ..utils import build_overview
from ..utils import build_event
from ..utils import build_model
from ..utils import build_html
from ..utils import manipulate_keys
from ..utils import manipulate_dates
from ..utils import format_objects
from ..utils import filter_objects
from ..utils import plot_peak_flux
from ..utils import plot_probability
from ..utils import tabulate_contingency_metrics
from ..utils import config

import pandas as pd
import datetime
import os
import shutil


def build_text(is_historical=False):
    """
    Writes the text that makes up the email body.

    Parameters
    ----------

    Returns
    -------
    html : string
    """
    
    # RESET IMAGES
    print(config.path.email_image)
    if os.path.exists(config.path.email_image):
        print('deleting...')
        shutil.rmtree(config.path.email_image)
    if not os.path.exists(config.path.email_image):
        os.mkdir(config.path.email_image)
   
    sphinx_df = pd.read_csv(os.path.join(config.path.dataframe, 'test-small.csv'))
    print('WARNING: dataframe is ' + config.path.dataframe + os.sep + 'test-small.csv')

    # CONVERT ALL DATAFRAME DATETIMES-LIKE STRINGS TO DATETIMES
    datetime_columns = manipulate_dates.identify_datetime_columns(sphinx_df)
    sphinx_df = manipulate_dates.convert_to_datetime(sphinx_df, datetime_columns)
    sphinx_df = filter_objects.categorize_column(sphinx_df, 'Model', 'Model Category', 'Model Flavor')

    # GET TIME BOUNDARIES
    week_start, week_end = manipulate_dates.get_mailsphinx_boundaries(config.time.week_first_day, config.time.week_last_day)
    year_start = pd.Timestamp(datetime.datetime(day=1, month=1, year=week_start.year, hour=0, minute=0, second=0, microsecond=0), tz='UTC')
    weekly_condition = (sphinx_df['Forecast Issue Time'] < week_end) * (sphinx_df['Forecast Issue Time'] >= week_start)
    yearly_condition = (sphinx_df['Forecast Issue Time'] < week_end) * (sphinx_df['Forecast Issue Time'] >= year_start)
    first_forecast_datetime = sphinx_df['Forecast Issue Time'].min()
    weekly_forecasts = sphinx_df[weekly_condition]
    yearly_forecasts = sphinx_df[yearly_condition] 

    # WRITE HTML
    html = ''
    html += build_html.build_head_section()
    html += build_overview.build_overview_section(sphinx_df, week_start, week_end, year_start, first_forecast_datetime, weekly_forecasts, yearly_forecasts)
    html += build_space_weather_summary.build_space_weather_summary(is_historical, start_datetime=week_start, end_datetime=week_end)
    event_forecasts, event = build_event.check_for_event(sphinx_df, week_start, week_end)
    if event:
        html += build_event.build_event_section(event_forecasts, week_end)
    html += build_model.build_model_section(sphinx_df, weekly_forecasts, week_start, week_end)

    return html

def build_text_new(is_historical=False):
    """
    Writes the text that makes up the email body.

    Parameters
    ----------

    Returns
    -------
    html : string
    """
    
    # RESET IMAGES
    print(config.path.email_image)
    if os.path.exists(config.path.email_image):
        print('deleting...')
        shutil.rmtree(config.path.email_image)
    if not os.path.exists(config.path.email_image):
        os.mkdir(config.path.email_image)
  

    sphinx_df = pd.read_csv(os.path.join(config.path.dataframe, 'test-small.csv'))
    print('WARNING: dataframe is ' + config.path.dataframe + os.sep + 'test-small.csv')

    # CONVERT ALL DATAFRAME DATETIMES-LIKE STRINGS TO DATETIMES
    datetime_columns = manipulate_dates.identify_datetime_columns(sphinx_df)
    sphinx_df = manipulate_dates.convert_to_datetime(sphinx_df, datetime_columns)
    sphinx_df = filter_objects.categorize_column(sphinx_df, 'Model', 'Model Category', 'Model Flavor')

    # GET TIME BOUNDARIES
    week_start, week_end = manipulate_dates.get_mailsphinx_boundaries(config.time.week_first_day, config.time.week_last_day)
    year_start = pd.Timestamp(datetime.datetime(day=1, month=1, year=week_start.year, hour=0, minute=0, second=0, microsecond=0), tz='UTC')
    weekly_condition = (sphinx_df['Forecast Issue Time'] < week_end) * (sphinx_df['Forecast Issue Time'] >= week_start)
    yearly_condition = (sphinx_df['Forecast Issue Time'] < week_end) * (sphinx_df['Forecast Issue Time'] >= year_start)
    first_forecast_datetime = sphinx_df['Forecast Issue Time'].min()
    weekly_forecasts = sphinx_df[weekly_condition]
    yearly_forecasts = sphinx_df[yearly_condition] 

    # WRITE HTML
    html = ''
    html += build_html.build_head_section()
    html += build_overview.build_overview_section(sphinx_df, week_start, week_end, year_start, first_forecast_datetime, weekly_forecasts, yearly_forecasts)
    html += build_space_weather_summary.build_space_weather_summary(is_historical, start_datetime=week_start, end_datetime=week_end)

    event_forecasts, event = build_event.check_for_event(sphinx_df, week_start, week_end)

    html += build_model.build_model_section_new(sphinx_df, weekly_forecasts, week_start, week_end) 
    #html += build_model.build_model_section(sphinx_df, weekly_forecasts, week_start, week_end)

    if event:
        html += build_event.build_event_section_new(event_forecasts, week_end)    
        #html += build_event.build_event_section(event_forecasts, week_end)
    
    return html

