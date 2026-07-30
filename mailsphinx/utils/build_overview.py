from ..utils import build_html
from ..utils import config
from ..utils import manipulate_keys
from ..utils import build_event

import os
import pandas as pd

# BUILD OVERVIEW SECTION
def build_overview_table_row(df, full_df, label_start_datetime, event_start_datetime, end_datetime, event_channel_labels, text=''):
    """
    Builds a table row for the Overview section of the email body.
    
    Parameters
    ----------
    df : pandas dataframe
        The forecast-issue-time-filtered segment (e.g. weekly_forecasts,
        yearly_forecasts, or the full sphinx_df) used for the existing
        forecast-count columns.

    full_df : pandas dataframe
        The full, unfiltered SPHINX dataframe. Event counts are
        computed from this, filtered by Observed SEP Threshold Crossing
        Time (not Forecast Issue Time), to match the semantics of the
        Events section and the new-events summary line.

    label_start_datetime : pandas Timestamp
        Start of this row's period, shown in the "Since ..." label.

    event_start_datetime : pandas Timestamp or None
        Lower bound for event counting. None means unbounded (used for
        "All Time", so every observed event is counted regardless of
        when the first forecast happened to be issued).

    end_datetime : pandas Timestamp
        Upper bound for event counting (shared across all rows -- the
        report's own end_datetime).

    event_channel_labels : list of string
        Ordered list of channel labels (e.g. "> 10 MeV, > 10 pfu") to
        show as columns, taken from config.order.energy_channel_threshold_order
        so column order is consistent across rows and reports.

    Returns
    -------
    row : list of string
    """
    row = []
    row.append(text + 'Since ' + label_start_datetime.strftime('%Y-%m-%d %H:%M'))
   
    # NUMBER OF FORECASTS 
    number_forecasts = len(df)
    row.append(str(number_forecasts))
    
    # NUMBER OF NOT CLEAR FORECASTS
    number_forecasts_not_clear = len(df[df['Predicted SEP All Clear'] == False])
    row.append(str(number_forecasts_not_clear))

    # NUMBER OF FORECASTS THAT PREDICTED PEAK FLUXES ABOVE THRESHOLD
    # INCLUDES FORECASTS THAT ONLY PREDICT MAX FLUX, ONLY PREDICT ONSET PEAK FLUX, OR BOTH
    if number_forecasts == 0:
        number_forecasts_above_threshold_peak_flux = 0
    else:
        thresholds = manipulate_keys.convert_threshold_key_to_float(df['Threshold Key'])
        above_threshold_peak_flux_condition = ((df['Predicted SEP Peak Intensity Max (Max Flux)'] >= thresholds) | (df['Predicted SEP Peak Intensity (Onset Peak)'] >= thresholds)) > 0
        number_forecasts_above_threshold_peak_flux = len(df[above_threshold_peak_flux_condition])
    row.append(str(number_forecasts_above_threshold_peak_flux))

    # NUMBER OF UNIQUE OBSERVED SEP EVENTS PER CONFIGURED CHANNEL, WITHIN
    # THIS ROW'S PERIOD (BY OBSERVED THRESHOLD CROSSING TIME, NOT
    # FORECAST ISSUE TIME -- SAME SEMANTICS AS THE EVENTS SECTION AND THE
    # NEW-EVENTS SUMMARY LINE, SO THE NUMBERS AGREE ACROSS THE REPORT).
    event_counts = build_event.count_unique_events_by_channel(
        full_df, start_datetime=event_start_datetime, end_datetime=end_datetime)
    for label in event_channel_labels:
        row.append(str(event_counts.get(label, 0)))

    df_columns = ['time_period', 'forecasts', 'not_clear_forecasts', 'above_threshold_peak_forecasts']
    df_dict = {}
    for i in range(0, len(df_columns)):
        df_dict[df_columns[i]] = [row[i]]
    out_df = pd.DataFrame(df_dict)
    for column in df_columns:
        if column != 'time_period':
            out_df[column] = out_df[column].astype(int)

    return row, out_df    

def build_overview_section(sphinx_df, week_start, week_end, year_start, first_forecast_datetime, weekly_forecasts, yearly_forecasts):
    """
    Writes the html that makes up the Overview section of the email body.

    Parameters
    ----------
    sphinx_df : SPHINX dataframe

    week_start : datetime

    week_end : datetime
    
    year_start : datetime
    
    weekly_forecasts : dataframe
    
    yearly_forecasts : dataframe
    
    Returns
    -------
    text : string
    """
    # ORDERED LIST OF CONFIGURED CHANNEL LABELS -- DEFINES COLUMN ORDER
    # FOR THE EVENT-COUNT COLUMNS, CONSISTENT ACROSS ALL THREE ROWS
    event_channel_labels = [
        build_event._channel_label(ek, tk)
        for ek, tk, _ in config.order.energy_channel_threshold_order
    ]

    # WRITE HTML TABLE FROM LIST OF LISTS
    table_data = []
    # "All Time" HAS NO LOWER BOUND ON EVENT COUNTING (None), SO EVERY
    # OBSERVED EVENT EVER IS COUNTED, REGARDLESS OF first_forecast_datetime
    dataframe_segments = [weekly_forecasts, yearly_forecasts, sphinx_df]
    start_segments = [week_start, year_start, first_forecast_datetime]
    event_start_segments = [week_start, year_start, None]
    texts = ['This Period: ', 'This Year: ', 'All Time: ']
    dfs = []
    for df, start, event_start, text in zip(dataframe_segments, start_segments, event_start_segments, texts):
        row, out_df = build_overview_table_row(df, sphinx_df, start, event_start, week_end, event_channel_labels, text)
        table_data.append(row)
        dfs.append(out_df) 
    headers = ['Time Period', 'Forecasts', 'Not Clear Forecasts', 'Above Threshold Peak Flux Forecasts'] + event_channel_labels
    text = build_html.build_section_title('Overview')
    text += build_html.build_table(headers, table_data)
    text += build_html.build_divider()

    return text
