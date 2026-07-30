from ..utils import build_html 
from ..utils import config
from ..utils import format_objects
from ..utils import manipulate_keys
from ..utils import scoreboard_call
from ..utils import tabulate_contingency_metrics

import pandas as pd

# BUILD EVENT SECTION
def check_for_event(df, start_datetime, end_datetime):
    df['Observed SEP Threshold Crossing Time'] = df['Observed SEP Threshold Crossing Time'].fillna(pd.NaT)
    event_forecasts = df[
        (df['Observed SEP All Clear'] == False) &
        (df['Observed SEP Threshold Crossing Time'] >= start_datetime) &
        (df['Observed SEP Threshold Crossing Time'] < end_datetime)
    ]
    # FILTER TO ONLY ENERGY CHANNEL / THRESHOLD PAIRS CONFIGURED FOR DISPLAY.
    # NORMALIZE ENERGY KEY TO STRIP REleASE MISMATCH SUFFIXES BEFORE COMPARING.
    configured = {(ek, tk) for ek, tk, _ in config.order.energy_channel_threshold_order}
    def _norm(key):
        return key.split('_min.')[0]
    event_forecasts = event_forecasts[
        event_forecasts.apply(
            lambda r: (_norm(r['Energy Channel Key']), r['Threshold Key']) in configured,
            axis=1)
    ]
    event = len(event_forecasts) > 0
    return event_forecasts, event 

def build_ccmc_scoreboard_links(event_forecasts, end_datetime):
    model_list = event_forecasts['Model'].unique().tolist()
    model_list.sort()
    url_probability = scoreboard_call.scoreboard_call(model_list, end_datetime, 'Probability')
    url_intensity = scoreboard_call.scoreboard_call(model_list, end_datetime, 'Intensity')
    text = build_html.build_html_shortlink(url_probability, 'CCMC SEP Probability Scoreboard') + '<br>'
    text += build_html.build_html_shortlink(url_intensity, 'CCMC SEP Intensity Scoreboard')
    return text

def _normalize_energy_key(energy_key):
    """Strip the mismatch suffix so REleASE mismatch keys group under
    their base channel."""
    return energy_key.split('_min.')[0]


def _channel_label(energy_key, threshold_key):
    """Return a human-readable label for an energy/threshold pair."""
    energy_str = manipulate_keys.convert_energy_key_to_string(energy_key)
    threshold_str = manipulate_keys.convert_threshold_key_to_string(threshold_key)
    return f'{energy_str}, {threshold_str}'


def count_unique_events_by_channel(df, start_datetime=None, end_datetime=None):
    """Count unique observed SEP events per configured (energy channel,
    threshold) pair within df, optionally restricted to threshold
    crossings within [start_datetime, end_datetime).

    Uses the same event definition, energy-key normalization, and
    mismatch exclusion as check_for_event/get_unique_events, so counts
    here are directly comparable to the Events section and to the
    per-channel breakdowns elsewhere in the report.

    Parameters
    ----------
    df : dataframe
        SPHINX dataframe (or any subset of it) to count events within.
    start_datetime, end_datetime : datetime or None
        If given, only threshold crossings in this range are counted.
        If both are None, every observed event in df is counted
        (suitable for an "All Time" count).

    Returns
    -------
    counts : dict
        Maps a channel label (e.g. "> 10 MeV, > 10 pfu") to the number
        of distinct observed events for that channel.
    """
    df = df.copy()
    df['Observed SEP Threshold Crossing Time'] = df['Observed SEP Threshold Crossing Time'].fillna(pd.NaT)

    mask = (df['Observed SEP All Clear'] == False)
    if start_datetime is not None:
        mask &= (df['Observed SEP Threshold Crossing Time'] >= start_datetime)
    if end_datetime is not None:
        mask &= (df['Observed SEP Threshold Crossing Time'] < end_datetime)
    event_forecasts = df[mask]

    configured = {(ek, tk) for ek, tk, _ in config.order.energy_channel_threshold_order}
    if event_forecasts.empty:
        return {}
    event_forecasts = event_forecasts[
        event_forecasts.apply(
            lambda r: (_normalize_energy_key(r['Energy Channel Key']), r['Threshold Key']) in configured,
            axis=1)
    ]
    if event_forecasts.empty:
        return {}

    unique_events = event_forecasts.drop_duplicates(
        subset=['Energy Channel Key', 'Threshold Key', 'Observed SEP Threshold Crossing Time'])
    unique_events = unique_events[unique_events['Mismatch Allowed'] == False]
    if unique_events.empty:
        return {}

    counts = {}
    for _, row in unique_events.iterrows():
        label = _channel_label(_normalize_energy_key(row['Energy Channel Key']), row['Threshold Key'])
        counts[label] = counts.get(label, 0) + 1
    return counts


def build_new_events_line(counts):
    """Build the "New SEP events in this period" summary line shown near
    the top of the report, directly beneath the evaluation period.

    Returns plain text/inline HTML with no block-level wrapper of its
    own -- this is substituted into the email header template's
    ${new_events_line}$ placeholder, which already sits inside a
    .paragraph_title div (the same style used for the generation time
    and evaluation period lines above it), so the sizing matches those
    two lines automatically.

    Parameters
    ----------
    counts : dict
        Output of count_unique_events_by_channel for the current
        report's period -- maps channel label to event count.

    Returns
    -------
    text : str
        Either "No new SEP events in this period." or a bold, red "New
        SEP events in this period:" label followed by the per-channel
        counts.
    """
    if not counts:
        return 'No new SEP events in this period.'
    channel_summary = '; '.join(f'{label} ({count})' for label, count in sorted(counts.items()))
    line = ('<b><span style="color:red;">New SEP events in this period:</span></b> '
            + channel_summary)
    return line


def get_unique_events(event_forecasts): 
    unique_events = event_forecasts.drop_duplicates(subset=['Energy Channel Key', 'Threshold Key', 'Observed SEP Threshold Crossing Time'])
    unique_events = unique_events[unique_events['Mismatch Allowed'] == False]
    observables = {'Energy': 'MeV',
                   'Flux Threshold': 'pfu',
                   'Observatory' : '', 
                   'Observed SEP Threshold Crossing Time' : '',
                   'Observed SEP End Time' : '',
                   'Observed SEP Duration' : 'hr',
                   'Observed SEP Fluence' : 'cm<sup>-2</sup>',
                   'Observed SEP Peak Intensity (Onset Peak)' : 'pfu',
                   'Observed SEP Peak Intensity (Onset Peak) Time' : '',
                   'Observed SEP Peak Intensity Max (Max Flux)' : 'pfu',
                   'Observed SEP Peak Intensity Max (Max Flux) Time' : ''
                  }

    unique_events['Energy Channel Key Surrogate'] = unique_events['Energy Channel Key'].apply(manipulate_keys.get_min_energy_threshold)
    unique_events['Threshold Key Surrogate'] = unique_events['Threshold Key'].apply(manipulate_keys.get_min_flux_threshold)
    unique_events['Observed SEP Threshold Crossing Time Surrogate'] = pd.to_datetime(unique_events['Observed SEP Threshold Crossing Time']).dt.strftime('%Y-%m-%d')
    unique_events['Energy'] = unique_events['Energy Channel Key Surrogate'].apply(format_objects.format_energy_threshold)
    unique_events['Flux Threshold'] = unique_events['Threshold Key Surrogate'].apply(format_objects.format_flux_threshold)
    unique_events = unique_events.sort_values(by=['Observed SEP Threshold Crossing Time Surrogate', 'Energy Channel Key Surrogate', 'Threshold Key Surrogate'])
    unique_events = unique_events.drop(columns=['Observed SEP Threshold Crossing Time Surrogate'])
    unique_events = format_objects.format_df_datetime(unique_events)
    return unique_events, observables
    
def build_event_summary(event_forecasts, base_indent=0):
    unique_events, observables = get_unique_events(event_forecasts)
    text = ''
    text += build_html.build_paragraph_title('Event Summary', base_indent=base_indent)
    headers = list(observables.keys())
    headers_with_units = []
    for key, value in observables.items():
        appendage = ''
        if value != '':
            appendage = '<br>[' + value + ']'
        headers_with_units.append(config.relabel.event_summary[key] + appendage)
    table_data = []
    table_data_color_dict = {}
    row_counter = 0
    for index, row in unique_events.iterrows():
        row_data = []
        for header in headers:
            row_data.append(format_objects.format_data(row[header]))
        table_data.append(row_data)
        for i in range(0, len(row_data)): 
            table_data_color_dict[(row_counter, i)] = config.color.associations['>=' + str(int(row['Energy Channel Key Surrogate'])) + ' MeV, >=' + str(int(row['Threshold Key Surrogate'])) + ' pfu Event']
        row_counter += 1
    text += build_html.build_table(headers_with_units, table_data, table_color_dict=table_data_color_dict)
    return text
    
def build_model_event_forecasts(event_forecasts):
    models = event_forecasts['Model Category'].unique().tolist()
    contingency_stat_header = ['Model Flavor', 'Observed SEP Threshold Crossing Time', 'Forecast Issue Time', 'Prediction Window Start', 'Prediction Window End']
    contingency_stat_display_header = ['Model Variant', 'Observed SEP Threshold Crossing Time', 'Forecast Issue Time', 'Prediction Window Start', 'Prediction Window End']
    text = build_html.build_paragraph_title('Model Forecasts')
    for model in models:
        text += build_html.build_paragraph_title(model, sublevel=1)
        df = event_forecasts[event_forecasts['Model Category'] == model]
        energies = df['Energy Channel Key'].unique().tolist()
        for energy in energies:
            text += build_html.build_paragraph_title(manipulate_keys.convert_energy_key_to_string(energy), sublevel=2)
            df_energy = df[df['Energy Channel Key'] == energy]
            text += tabulate_contingency_metrics.build_single_stat_contingency_table(df_energy, mode='hit', header=contingency_stat_header, display_header=contingency_stat_display_header)
            text += tabulate_contingency_metrics.build_single_stat_contingency_table(df_energy, mode='miss', header=contingency_stat_header, display_header=contingency_stat_display_header)
    return text

def build_event_section(event_forecasts, end_datetime):
    text = ''
    text += build_html.build_section_title('Events')
    text += build_html.build_paragraph_title('Scoreboard Links')
    text += build_ccmc_scoreboard_links(event_forecasts, end_datetime)
    text += build_event_summary(event_forecasts)
    text += build_html.build_divider()
    return text
