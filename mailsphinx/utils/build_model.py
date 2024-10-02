from ..utils import build_html
from ..utils import build_legend
from ..utils import config
from ..utils import filter_objects
from ..utils import manipulate_keys
from ..utils import plot_advanced_warning
from ..utils import plot_contingency
from ..utils import plot_peak_flux
from ..utils import plot_probability
from ..utils import tabulate_contingency_metrics

import numpy as np
import os


def build_model_section(df, weekly_df, week_start, week_end, events, convert_images_to_base64=False):
    text = build_html.build_section_title('Model Performance')

    # MAKE CONTINGENCY TIMELINES
    text += build_html.build_paragraph_title('SEP All Clear Contingency Timelines')
    counter = 0
    for energy_key, energy_group in weekly_df.groupby('Energy Channel Key'):
        energy_channel_string = manipulate_keys.convert_energy_key_to_string(energy_key) 
        if energy_group['Energy Channel Key'].eq(energy_key).any():
            text += build_html.build_paragraph_title(energy_channel_string, sublevel=1)
            for model_category, group in energy_group.groupby('Model Category'):
                for model_flavor, subgroup in group.groupby('Model Flavor'):
                    for threshold_key, subsubgroup in subgroup.groupby('Threshold Key'):
                        filtered_events = events[(events['Energy Channel Key'] == energy_key) & (events['Threshold Key'] == threshold_key)]
                        threshold_string = manipulate_keys.convert_threshold_key_to_string(threshold_key)
                        if model_flavor == '':
                            space = ''
                        else:
                            space = ' '
                        title = model_category + space + model_flavor.replace('_', ' ') + ', ' + energy_channel_string + ', ' + threshold_string
                        text += plot_contingency.build_contingency_plot(title, subsubgroup, os.path.join(config.path.email_image, 'contingency-' + str(counter) + '.jpg'), week_start, week_end, filtered_events, convert_image_to_base64=convert_images_to_base64)
                        counter += 1

    # MAKE ADVANCED WARNING TIMELINES
    if len(events) > 0:
        counter = 0
        text += build_html.build_paragraph_title('Advanced Warning Time Comparison')
        for energy_key, energy_group in weekly_df.groupby('Energy Channel Key'):
            energy_channel_string = manipulate_keys.convert_energy_key_to_string(energy_key) 
            if energy_group['Energy Channel Key'].eq(energy_key).any():
                energy_reached = True
                for threshold_key, group in energy_group.groupby('Threshold Key'):
                    filtered_events = events[(events['Energy Channel Key'] == energy_key) & (events['Threshold Key'] == threshold_key)]
                    for event_key, event_group in filtered_events.groupby('Observed SEP Threshold Crossing Time'):
                        if energy_reached:
                            text += build_html.build_paragraph_title(energy_channel_string, sublevel=1)
                            energy_reached = False
                        title = 'Event starting on ' + event_key.strftime('%Y-%m-%d %H:%M:%S')
                        text += plot_advanced_warning.build_advanced_warning_plot(title, group, os.path.join(config.path.email_image, 'advanced-warning-' + str(counter) + '.jpg'), week_start, week_end, event_group, convert_image_to_base64=convert_images_to_base64)
                        counter += 1

    # MAKE PROBABILITY TIMELINES WITH VERTICAL HISTOGRAMS
    text += build_html.build_paragraph_title('SEP Probability Timelines')
    counter = 0
    for energy_key, energy_group in weekly_df.groupby('Energy Channel Key'):
        energy_channel_string = manipulate_keys.convert_energy_key_to_string(energy_key)
        if not filter_objects.is_column_empty(energy_group, 'Predicted SEP Probability'):
            text += build_html.build_paragraph_title(energy_channel_string, sublevel=1)
            for name, group in energy_group.groupby('Model Category'):
                if not filter_objects.is_column_empty(group, 'Predicted SEP Probability'):
                    filtered_events = events[(events['Energy Channel Key'] == energy_key)]
                    unique_model_flavors = group['Model Flavor'].unique()
                    unique_model_flavors_with_probability = []
                    for model_flavor in unique_model_flavors:
                        if not filter_objects.is_column_empty(group[group['Model Flavor'] == model_flavor], 'Predicted SEP Probability'):
                            unique_model_flavors_with_probability.append(model_flavor)

                    need_legend = len(unique_model_flavors_with_probability) > 1
                    if not need_legend:
                        subname = ' ' + unique_model_flavors[0]
                    else:
                        subname = ''
                    text += plot_probability.build_probability_plot(name + subname + ', ' + energy_channel_string, group, os.path.join(config.path.email_image, 'probability-histogram-' + str(counter) + '.jpg'), week_start, week_end, filtered_events, need_legend=need_legend, convert_image_to_base64=convert_images_to_base64)
                    counter += 1

    # MAKE PREDICTED PEAK FLUX VS. OBSERVED PEAK FLUX
    # DETERMINE MIN/MAX VALUES
    # IMPORTANT VALUES
    # Observed SEP Peak Intensity (Onset Peak)
    # Observed SEP Peak Intensity Max (Max Flux)
    # Observed Max Flux in Prediction Window
    # Predicted SEP Peak Intensity (Onset Peak)
    # Predicted SEP Peak Intensity Max (Max Flux)
    counter = 0
    at_least_one_plot = True
    for name, group in weekly_df.groupby('Energy Channel Key'):
        energy_channel_string = manipulate_keys.convert_energy_key_to_string(name)
        for subname, subgroup in group.groupby('Threshold Key'):
            threshold_flux_string = manipulate_keys.convert_threshold_key_to_string(subname)
            threshold_flux = float(threshold_flux_string.lstrip('> ').rstrip(' pfu'))
            is_onset_peak_empty = (filter_objects.is_column_empty(subgroup, 'Predicted SEP Peak Intensity (Onset Peak)')) or (filter_objects.is_column_empty(subgroup, 'Observed SEP Peak Intensity (Onset Peak)'))
            is_predicted_max_flux_empty = filter_objects.is_column_empty(subgroup, 'Predicted SEP Peak Intensity Max (Max Flux)')

            is_max_flux_empty = (is_predicted_max_flux_empty) or (filter_objects.is_column_empty(subgroup, 'Observed SEP Peak Intensity Max (Max Flux)'))
            is_max_flux_in_prediction_window_empty = (is_predicted_max_flux_empty) or filter_objects.is_column_empty(subgroup, 'Observed Max Flux in Prediction Window')
            if is_onset_peak_empty and is_max_flux_empty and is_max_flux_in_prediction_window_empty:
                plot_exists = False
            else:
                plot_path = os.path.join(config.path.email_image, 'predicted-peak-flux-vs-observed-peak-flux-' + str(counter) + '.jpg')
                counter += 1
                plot_exists, plot_text = plot_peak_flux.build_peak_flux_plot(energy_channel_string, threshold_flux_string, subgroup, plot_path, threshold_flux, convert_image_to_base64=convert_images_to_base64)
            if plot_exists:
                if at_least_one_plot:
                    at_least_one_plot = False
                    text += build_html.build_paragraph_title('Predicted Peak Flux vs. Observed Peak Flux')
                    build_legend.build_legend_peak_flux_separate()
                    text += build_html.build_image(os.path.join(config.path.email_image, 'legend-peak-flux.jpg'), write_as_base64=convert_images_to_base64)
                text += plot_text
    text += build_html.build_divider()
    return text



