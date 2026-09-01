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


# COLUMNS ACTUALLY REFERENCED BY MAILSPHINX'S build_* / plot_* / tabulate_*
# MODULES, CONFIRMED BY AUDITING EVERY DIRECT COLUMN ACCESS ACROSS THE
# CODEBASE (NOT DERIVED FROM config.type.dataframe, WHICH IS DECLARED BUT
# NEVER ACTUALLY USED ANYWHERE). 'Model Category'/'Model Flavor' AND OTHER
# *Surrogate/COMPUTED COLUMNS ARE DELIBERATELY EXCLUDED -- THEY'RE
# COMPUTED FROM 'Model' (VIA filter_objects.categorize_column) AFTER
# LOADING, NOT READ DIRECTLY.
MAILSPHINX_NEEDED_COLUMNS = [
    'Model',
    'Energy Channel Key',
    'Threshold Key',
    'Mismatch Allowed',
    'Forecast Issue Time',
    'Prediction Window Start',
    'Prediction Window End',
    'Observed SEP All Clear',
    'Predicted SEP All Clear',
    'All Clear Match Status',
    'Observed SEP Threshold Crossing Time',
    'Observed SEP End Time',
    'Observed SEP Duration',
    'Observed SEP Fluence',
    'Observed SEP Peak Intensity (Onset Peak)',
    'Observed SEP Peak Intensity (Onset Peak) Time',
    'Observed SEP Peak Intensity Max (Max Flux)',
    'Observed SEP Peak Intensity Max (Max Flux) Time',
    'Predicted SEP Peak Intensity (Onset Peak)',
    'Predicted SEP Peak Intensity Max (Max Flux)',
    'Predicted SEP Probability',
    'Observatory',
]


def _load_sphinx_df_from_partitions(partition_path):
    """ Read only MAILSPHINX_NEEDED_COLUMNS directly from the partitioned
        Parquet data written by sphinxval, instead of loading the full
        flat SPHINX_evaluated.pkl (70+ columns).

        UNLIKE pushvivid's conversion code, mailsphinx genuinely needs
        ALL-TIME history (see build_overview.py's "All Time" row) --
        there is no bounded date range to filter by at read time. This
        narrows COLUMNS, not ROWS: every partition file still gets read,
        just with a much smaller width. Total row count, and therefore
        the irreducible part of peak memory, is unchanged from the flat
        pkl approach -- this reduces memory per row, not the number of
        rows held at once.

        Uses partition_io.py, VENDORED into this repo (utils/
        partition_io.py, alongside this file) rather than imported live
        from the sphinxval repo. sphinxval, pushvivid, and mailsphinx are
        separate git repositories -- a live cross-repo import has no
        version pinning, is invisible to this repo's own tests, and
        breaks if sphinxval's internal layout changes (this happened
        once already). See partition_io.py's own module docstring for
        the full rationale. If you fix a bug in partition_io.py,
        propagate the same fix to all three vendored copies (sphinxval,
        pushvivid, mailsphinx).

        NOTE: mailsphinx uses its OWN separate venv (see run_mailsphinx.sh:
        "mailsphinx USES ITS OWN VENV, SEPARATE FROM THE SHARED PIPELINE
        VENV"). pandas and pyarrow must be installed there for this
        import to succeed -- partition_io.py's dependency footprint is
        deliberately small (pandas, pyarrow, astropy.units only).
    """
    from ..utils import partition_io

    print(f'Reading {len(MAILSPHINX_NEEDED_COLUMNS)} columns directly from '
          f'partitions at {partition_path} (no full flat pkl loaded).')
    df = partition_io.read_all_partitions(partition_path, 'SPHINX_evaluated',
        columns=MAILSPHINX_NEEDED_COLUMNS)
    return df


def custom_warning_handler(message, category, filename, lineno, file=None, line=None):
    print('Warning: ', message)
    print('Category: ', category.__name__)
    print('File: ', filename, 'Line: ', lineno)
    traceback.print_stack()

def build_text(start_datetime, end_datetime, convert_images_to_base64=False, dataframe_filename=None, partition_path=None):
    """
    Writes the text that makes up the email body.

    Parameters
    ----------
    start_datetime : datetime
    end_datetime : datetime
    convert_images_to_base64 : bool
    dataframe_filename : str or None
        Path to a flat SPHINX_evaluated.pkl. Ignored if partition_path is
        given.
    partition_path : str or None
        Directory holding sphinxval's partitioned SPHINX_evaluated data.
        If given, only MAILSPHINX_NEEDED_COLUMNS are read directly from
        partitions -- the full flat pkl is never loaded. Takes
        precedence over dataframe_filename if both are given.

    Returns
    -------
    html : string
    event : bool
        True if an observed SEP event occurred during
        [start_datetime, end_datetime), False otherwise (including
        when there is no data to evaluate at all).
    """
    #warnings.simplefilter('always', category=RuntimeWarning)
    #warnings.showwarning = custom_warning_handler

    warnings.filterwarnings('ignore', category=pd.errors.DtypeWarning)
    if partition_path:
        sphinx_df = _load_sphinx_df_from_partitions(partition_path)
    else:
        sphinx_df = pd.read_pickle(dataframe_filename)

    # EXCLUDE MODELS
    for model in config.exclude_models:
        sphinx_df = sphinx_df[sphinx_df['Model'] != model]

    # CONVERT ALL DATAFRAME DATETIMES-LIKE STRINGS TO DATETIMES
    for col in sphinx_df.select_dtypes(include=['datetime64[ns]']):
        sphinx_df[col] = sphinx_df[col].dt.tz_localize('UTC')
    sphinx_df = filter_objects.categorize_column(sphinx_df, 'Model', 'Model Category', 'Model Flavor')

    event = False
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

        # CHECK FOR NEW EVENTS IN THIS REPORT'S PERIOD BEFORE BUILDING THE
        # HEADER, SO THE NEW-EVENTS SUMMARY LINE CAN BE SHOWN IMMEDIATELY
        # BENEATH THE EVALUATION PERIOD. REUSED BELOW FOR THE Events
        # SECTION FURTHER DOWN, SO THIS IS ONLY COMPUTED ONCE.
        event_forecasts, event = build_event.check_for_event(sphinx_df, start_datetime, end_datetime)
        events, _ = build_event.get_unique_events(event_forecasts)
        new_event_counts = build_event.count_unique_events_by_channel(
            sphinx_df, start_datetime=start_datetime, end_datetime=end_datetime)

        # WRITE HTML
        html = ''
        new_events_line_html = build_event.build_new_events_line(new_event_counts)
        html += build_html.build_head_section(new_events_line=new_events_line_html)

        # TABLE OF CONTENTS — LIST TOP-LEVEL SECTIONS WITH JUMP LINKS.
        # THE REleASE NOTE APPEARS HERE SINCE IT APPLIES ACROSS SECTIONS.
        toc_sections = [
            'Overview',
            'All Clear Contingency Tables',
            'Space Weather Summary',
            'Model Performance Timelines',
            'Metrics Summary',
            'Evaluation Breakdown',
        ]
        has_release = sphinx_df['Model'].str.contains('REleASE', case=False, na=False).any()
        release_note = None
        if has_release:
            release_note = (
                '<em>Note on HESPERIA REleASE:</em> REleASE forecasts of '
                '15.8&#8209;39.8&nbsp;MeV protons exceeding 0.1&nbsp;pfu/MeV are validated '
                'here against &gt;10&nbsp;MeV protons exceeding 10&nbsp;pfu. REleASE '
                'forecasts of 28.2&#8209;50.1&nbsp;MeV protons exceeding 0.1&nbsp;pfu/MeV '
                'are validated against both &gt;10&nbsp;MeV protons exceeding 10&nbsp;pfu '
                'and &gt;100&nbsp;MeV protons exceeding 1&nbsp;pfu. Predicted peak fluxes '
                'from REleASE may be correlated with observed values but are not expected '
                'to match numerically, as they represent different energy channels and units.'
            )
        html += build_html.build_toc(toc_sections, notes=release_note)

        html += build_overview.build_overview_section(sphinx_df, start_datetime, end_datetime, year_start, first_forecast_datetime, weekly_forecasts, yearly_forecasts)
        event_forecasts, event = build_event.check_for_event(sphinx_df, start_datetime, end_datetime)
        events, _ = build_event.get_unique_events(event_forecasts)
        if event:
            html += build_event.build_event_section(event_forecasts, start_datetime, end_datetime)
        contingency_html, breakdown_sections = tabulate_contingency_metrics.build_all_clear_contingency_table(sphinx_df, start_datetime, end_datetime)
        html += contingency_html
        html += build_space_weather_summary.build_space_weather_summary(start_datetime=start_datetime, end_datetime=end_datetime, convert_image_to_base64=convert_images_to_base64)
        html += build_model.build_model_section(sphinx_df, weekly_forecasts, start_datetime, end_datetime, events, convert_images_to_base64)
        html += build_metrics.build_metrics_section(sphinx_df)
        html += build_evaluation_breakdown.build_evaluation_breakdown(breakdown_sections)
    return html, event
