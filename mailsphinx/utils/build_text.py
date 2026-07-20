from ..utils import build_evaluation_breakdown
from ..utils import build_event
from ..utils import build_html
from ..utils import build_metrics
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

def build_text(start_datetime, end_datetime, convert_images_to_base64=False, dataframe_filename=None):
    """
    Writes the text that makes up the email body.

    Parameters
    ----------
    start_datetime : datetime
    end_datetime : datetime
    convert_images_to_base64 : bool
    dataframe_filename : str or None

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
        config.time.start_time = start_datetime
        config.time.end_time = end_datetime
        year_start = pd.to_datetime(datetime.datetime(day=1, month=1, year=start_datetime.year, hour=0, minute=0, second=0, microsecond=0), utc=True)
        weekly_condition = (sphinx_df['Forecast Issue Time'] < end_datetime) & (sphinx_df['Forecast Issue Time'] >= start_datetime)
        yearly_condition = (sphinx_df['Forecast Issue Time'] < end_datetime) & (sphinx_df['Forecast Issue Time'] >= year_start)
        first_forecast_datetime = sphinx_df['Forecast Issue Time'].min()
        weekly_forecasts = sphinx_df[weekly_condition]
        yearly_forecasts = sphinx_df[yearly_condition]

        # SORT BY ENERGY CHANNEL KEY
        weekly_forecasts['Energy Channel Key'] = pd.Categorical(weekly_forecasts['Energy Channel Key'], categories=config.order.energy_key_order, ordered=True)
        weekly_forecasts = weekly_forecasts.sort_values('Energy Channel Key')

        # WRITE HTML
        html = ''
        html += build_html.build_head_section()

        # TABLE OF CONTENTS — LIST TOP-LEVEL SECTIONS WITH JUMP LINKS.
        # THE REleASE NOTE APPEARS HERE SINCE IT APPLIES ACROSS SECTIONS.
        toc_sections = [
            'Overview',
            'All Clear Contingency Tables',
            'Space Weather Summary',
            'Model Performance',
            'Metrics Summary',
            'Evaluation Breakdown',
        ]
        has_release = sphinx_df['Model'].str.contains('REleASE', case=False, na=False).any()
        release_note = None
        if has_release:
            release_note = (
                '<em>Note on HESPERIA REleASE:</em> REleASE forecasts are issued for '
                '15.8&#8209;39.8&nbsp;MeV protons exceeding 0.1&nbsp;pfu/MeV, but are '
                'validated here against &gt;10&nbsp;MeV protons exceeding 10&nbsp;pfu. '
                'Predicted peak fluxes from REleASE may be correlated with observed values '
                'but are not expected to match numerically, as they represent different '
                'energy channels and units.'
            )
        html += build_html.build_toc(toc_sections, notes=release_note)

        html += build_overview.build_overview_section(sphinx_df, start_datetime, end_datetime, year_start, first_forecast_datetime, weekly_forecasts, yearly_forecasts)
        event_forecasts, event = build_event.check_for_event(sphinx_df, start_datetime, end_datetime)
        events, _ = build_event.get_unique_events(event_forecasts)
        if event:
            html += build_event.build_event_section(event_forecasts, end_datetime)
        contingency_html, breakdown_sections = tabulate_contingency_metrics.build_all_clear_contingency_table(sphinx_df, start_datetime, end_datetime)
        html += contingency_html
        html += build_space_weather_summary.build_space_weather_summary(start_datetime=start_datetime, end_datetime=end_datetime, convert_image_to_base64=convert_images_to_base64)
        html += build_model.build_model_section(sphinx_df, weekly_forecasts, start_datetime, end_datetime, events, convert_images_to_base64)
        html += build_metrics.build_metrics_section(sphinx_df)
        html += build_evaluation_breakdown.build_evaluation_breakdown(breakdown_sections)
    return html
