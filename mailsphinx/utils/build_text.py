from ..utils import build_event
from ..utils import build_html
from ..utils import build_model
from ..utils import build_overview
from ..utils import build_space_weather_summary
from ..utils import config
from ..utils import filter_objects
from ..utils import manipulate_dates
from ..utils import tabulate_contingency_metrics

import datetime
import os
import pandas as pd
import pickle
import shutil
import traceback
import warnings

pd.options.mode.chained_assignment = None



def custom_warning_handler(message, category, filename, lineno, file=None, line=None):
    print('Warning: ', message)
    print('Category: ', category.__name__)
    print('File: ', filename, 'Line: ', lineno)
    traceback.print_stack()

def build_text(is_historical=False, convert_images_to_base64=False, start_datetime=None, end_datetime=None, dataframe_filename=None):
    """
    Writes the text that makes up the email body.

    Parameters
    ----------

    Returns
    -------
    html : string
    """
    #warnings.simplefilter('always', category=RuntimeWarning)   
    #warnings.showwarning = custom_warning_handler 

    warnings.filterwarnings('ignore', category=pd.errors.DtypeWarning)
    sphinx_df = pd.read_pickle(dataframe_filename)

    # EXCLUDE MODELS
    for model in config.exclude_models:
        sphinx_df = sphinx_df[sphinx_df['Model'] != model]

    # CONVERT ALL DATAFRAME DATETIMES-LIKE STRINGS TO DATETIMES
    for col in sphinx_df.select_dtypes(include=['datetime64[ns]']):
        sphinx_df[col] = sphinx_df[col].dt.tz_localize('UTC')
    sphinx_df = filter_objects.categorize_column(sphinx_df, 'Model', 'Model Category', 'Model Flavor')


    if sphinx_df.empty:
        html = ''
    else:
        # GET TIME BOUNDARIES
        if is_historical:
            week_start = pd.to_datetime(start_datetime, utc=True)
            week_end = pd.to_datetime(end_datetime, utc=True)
        else:
            week_start, week_end = manipulate_dates.get_mailsphinx_boundaries(config.time.week_first_day, config.time.week_last_day)
        year_start = pd.to_datetime(datetime.datetime(day=1, month=1, year=week_start.year, hour=0, minute=0, second=0, microsecond=0), utc=True)
        weekly_condition = (sphinx_df['Forecast Issue Time'] < week_end) & (sphinx_df['Forecast Issue Time'] >= week_start)
        yearly_condition = (sphinx_df['Forecast Issue Time'] < week_end) & (sphinx_df['Forecast Issue Time'] >= year_start)
        first_forecast_datetime = sphinx_df['Forecast Issue Time'].min()
        weekly_forecasts = sphinx_df[weekly_condition]
        yearly_forecasts = sphinx_df[yearly_condition] 

        # SORT BY ENERGY CHANNEL KEY
        weekly_forecasts['Energy Channel Key'] = pd.Categorical(weekly_forecasts['Energy Channel Key'], categories=config.order.energy_key_order, ordered=True)
        weekly_forecasts = weekly_forecasts.sort_values('Energy Channel Key')

        # WRITE HTML
        html = ''
        html += build_html.build_head_section()
        html += build_overview.build_overview_section(sphinx_df, week_start, week_end, year_start, first_forecast_datetime, weekly_forecasts, yearly_forecasts)
        event_forecasts, event = build_event.check_for_event(sphinx_df, week_start, week_end)
        events, _ = build_event.get_unique_events(event_forecasts)
        if event:
            html += build_event.build_event_section(event_forecasts, week_end) 
        html += tabulate_contingency_metrics.build_all_clear_contingency_table(sphinx_df, week_start, week_end)
        html += build_space_weather_summary.build_space_weather_summary(is_historical, start_datetime=week_start, end_datetime=week_end, convert_image_to_base64=convert_images_to_base64)
        html += build_model.build_model_section(sphinx_df, weekly_forecasts, week_start, week_end, events, convert_images_to_base64) 
    return html

