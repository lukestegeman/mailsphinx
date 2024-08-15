from ..utils import build_html 
from ..utils import scoreboard_call
from ..utils import manipulate_keys
from ..utils import format_objects
from ..utils import tabulate_contingency_metrics

import pandas as pd

# BUILD EVENT SECTION
def check_for_event(df, start_datetime, end_datetime):
    event_forecasts = df[(df['Observed SEP All Clear'] == False) & (df['Observed SEP Threshold Crossing Time'] >= start_datetime) & (df['Observed SEP Threshold Crossing Time'] < end_datetime)]
    if len(event_forecasts) > 0:
        event = True
    else:
        event = False 
    return event_forecasts, event 

def build_ccmc_scoreboard_links(event_forecasts, end_datetime):
    model_list = event_forecasts['Model'].unique().tolist()
    model_list.sort()
    url_probability = scoreboard_call.scoreboard_call(model_list, end_datetime, 'Probability')
    url_intensity = scoreboard_call.scoreboard_call(model_list, end_datetime, 'Intensity')
    text = build_html.build_html_shortlink(url_probability, 'CCMC SEP Probability Scoreboard') + '<br>'
    text += build_html.build_html_shortlink(url_intensity, 'CCMC SEP Intensity Scoreboard')
    return text

def build_event_summary(event_forecasts, base_indent=0):
    unique_events = event_forecasts.drop_duplicates(subset=['Energy Channel Key', 'Threshold Key', 'Observed SEP Threshold Crossing Time'])
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
    unique_events = unique_events.drop(columns=['Observed SEP Threshold Crossing Time Surrogate', 'Energy Channel Key Surrogate', 'Threshold Key Surrogate'])
    unique_events = format_objects.format_df_datetime(unique_events) 
    text = ''
    text += build_html.build_paragraph_title('Event Summary', base_indent=base_indent)
    headers = list(observables.keys())
    headers_with_units = []
    for key, value in observables.items():
        appendage = ''
        if value != '':
            appendage = ' [' + value + ']'
        headers_with_units.append(key + appendage)
    table_data = []
    for index, row in unique_events.iterrows():
        row_data = []
        for header in headers:
            row_data.append(format_objects.format_data(row[header]))
        table_data.append(row_data)
    text += build_html.build_table(headers_with_units, table_data)
    return text
    
def build_model_event_forecasts(event_forecasts):
    models = event_forecasts['Model Category'].unique().tolist()
    contingency_stat_header = ['Model Flavor', 'Observed SEP Threshold Crossing Time', 'Forecast Issue Time', 'Prediction Window Start', 'Prediction Window End']
    text = build_html.build_paragraph_title('Model Forecasts')
    for model in models:
        text += build_html.build_paragraph_title(model, sublevel=1)
        df = event_forecasts[event_forecasts['Model Category'] == model]
        energies = df['Energy Channel Key'].unique().tolist()
        for energy in energies:
            text += build_html.build_paragraph_title(manipulate_keys.convert_energy_key_to_string(energy), sublevel=2)
            df_energy = df[df['Energy Channel Key'] == energy]
            text += tabulate_contingency_metrics.build_single_stat_contingency_table(df_energy, mode='hit', header=contingency_stat_header)
            text += tabulate_contingency_metrics.build_single_stat_contingency_table(df_energy, mode='miss', header=contingency_stat_header)
    return text

def build_event_section(event_forecasts, end_datetime):
    text = ''
    text += build_html.build_section_title('Events')
    text += build_html.build_paragraph_title('Scoreboard Links')
    text += build_ccmc_scoreboard_links(event_forecasts, end_datetime)
    text += build_event_summary(event_forecasts)
    text += build_model_event_forecasts(event_forecasts) 
    text += build_html.build_divider()
    return text
