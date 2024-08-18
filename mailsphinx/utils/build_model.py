from ..utils import build_html
from ..utils import tabulate_contingency_metrics
from ..utils import plot_peak_flux
from ..utils import plot_probability
from ..utils import plot_contingency
from ..utils import filter_objects
from ..utils import manipulate_keys
from ..utils import config

import os
import numpy as np

def build_model_section(df, weekly_df, week_start, week_end):
    text = build_html.build_section_title('Model Performance')
    text += tabulate_contingency_metrics.build_all_clear_contingency_table(df, week_start, week_end)
    #text += tabulate_contingency_metrics.build_false_alarm_table(weekly_df)
    counter = 0
    for name, group in weekly_df.groupby('Energy Channel Key'):
        text += plot_peak_flux.build_peak_flux_plot(group, os.path.join(config.path.email_image, f'predicted-peak-flux-vs-observed-peak-flux-' + str(counter) + '.jpg'))
        counter += 1
    counter = 0
    text += build_html.build_paragraph_title('Probability Histograms')
    for name, group in weekly_df.groupby('Model Category'): 
        if not filter_objects.is_column_empty(group, 'Predicted SEP Probability'):
            text += plot_probability.build_probability_plot(group, os.path.join(config.path.email_image, 'probability-histogram-' + str(counter) + '.jpg'))
    return text

def build_model_section_new(df, weekly_df, week_start, week_end, events):
    text = build_html.build_section_title('Model Performance')

    # MAKE CONTINGENCY TIMELINES
    text += build_html.build_paragraph_title('SEP All Clear Contingency Timelines')
    counter = 0
    for model_category, group in weekly_df.groupby('Model Category'):
        for model_flavor, subgroup in group.groupby('Model Flavor'):
            for energy_key, subsubgroup in subgroup.groupby('Energy Channel Key'):
                energy_channel_string = manipulate_keys.convert_energy_key_to_string(energy_key)
                for threshold_key, subsubsubgroup in subsubgroup.groupby('Threshold Key'):
                    filtered_events = events[(events['Energy Channel Key'] == energy_key) & (events['Threshold Key'] == threshold_key)]
                    threshold_string = manipulate_keys.convert_threshold_key_to_string(threshold_key)
                    if model_flavor == '':
                        space = ''
                    else:
                        space = ' '
                    title = model_category + space + model_flavor.replace('_', ' ') + ', ' + energy_channel_string + ', ' + threshold_string
                    text += plot_contingency.build_contingency_plot(title, subsubsubgroup, os.path.join(config.path.email_image, 'contingency-' + str(counter) + '.jpg'), week_start, week_end, filtered_events)
                    counter += 1

    # MAKE PROBABILITY TIMELINES WITH VERTICAL HISTOGRAMS
    text += build_html.build_paragraph_title('SEP Probability Timelines')
    counter = 0
    for name, group in weekly_df.groupby('Model Category'):
        for energy_key, subgroup in group.groupby('Energy Channel Key'):
            if not filter_objects.is_column_empty(subgroup, 'Predicted SEP Probability'):
                filtered_events = events[(events['Energy Channel Key'] == energy_key)]
                energy_channel_string = manipulate_keys.convert_energy_key_to_string(energy_key)
                unique_model_flavors = subgroup['Model Flavor'].unique()
                need_legend = len(unique_model_flavors) > 1
                if not need_legend:
                    subname = ' ' + unique_model_flavors[0]
                else:
                    subname = ''
                text += plot_probability.build_probability_plot(name + subname + ', ' + energy_channel_string, subgroup, os.path.join(config.path.email_image, 'probability-histogram-' + str(counter) + '.jpg'), week_start, week_end, filtered_events, need_legend=need_legend)
                counter += 1

    # MAKE PREDICTED PEAK FLUX VS. OBSERVED PEAK FLUX
    text += build_html.build_paragraph_title('Predicted Peak Flux vs. Observed Peak Flux')
    counter = 0
    
    
    # DETERMINE MIN/MAX VALUES
    predicted_peak = weekly_df['Predicted SEP Peak Intensity (Onset Peak)']
    observed_peak = weekly_df['Observed SEP Peak Intensity (Onset Peak)']
    min_predicted = np.min(predicted_peak)
    max_predicted = np.max(predicted_peak)
    min_observed = np.min(observed_peak)
    max_observed = np.max(observed_peak)
    min_peak = min(min_predicted, min_observed)
    max_peak = max(max_predicted, max_observed)

    for name, group in weekly_df.groupby('Energy Channel Key'):
        if not filter_objects.is_column_empty(group, 'Predicted SEP Peak Intensity (Onset Peak)'):
            energy_channel_string = manipulate_keys.convert_energy_key_to_string(name)
            text += plot_peak_flux.build_peak_flux_plot(energy_channel_string, group, os.path.join(config.path.email_image, 'predicted-peak-flux-vs-observed-peak-flux-' + str(counter) + '.jpg'), min_peak, max_peak)
            counter += 1

    # MAKE CONTINGENCY TABLE
    text += tabulate_contingency_metrics.build_all_clear_contingency_table(df, week_start, week_end)

    text += build_html.build_divider()

    return text



