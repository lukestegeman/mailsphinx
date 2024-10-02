from ..utils import build_html
from ..utils import config
from ..utils import filter_objects

import numpy as np
import matplotlib
import matplotlib.pyplot as plt

plt.rcParams['font.family'] = config.plot.font
plt.rcParams['font.size'] = config.plot.fontsize

def build_peak_flux_plot(energy_channel_string, threshold_flux_string, df, savefile, threshold_flux, convert_image_to_base64=False):
    plot_exists, table_data, table_color_dict, table_text_color_dict = plot_predicted_peak_flux_vs_observed_peak_flux(energy_channel_string, threshold_flux_string, df, savefile, threshold_flux)
    text = ''
    if plot_exists:
        text += build_html.build_image(savefile, write_as_base64=convert_image_to_base64)
        headers = ['Data Type', 'Model Category', 'Hits', 'Misses', 'False Alarms', 'Correct Negatives', 'Peak Flux Forecasts']
        header_color_dict = dict(zip(headers, [None, None, config.color.associations['Hits'], config.color.associations['Misses'], config.color.associations['False Alarms'], config.color.associations['Correct Negatives'], None]))
        
        text += build_html.build_table(headers, table_data, header_color_dict=header_color_dict, table_color_dict=table_color_dict, table_text_color_dict=table_text_color_dict)
    return plot_exists, text

def plot_predicted_peak_flux_vs_observed_peak_flux(energy_channel_string, threshold_flux_string, df, save, threshold_flux):
    color_counter = 0
    row_counter = 0
    plot_exists = False
    figure_created = False
    min_predicted_peak = 1.0e+99
    max_predicted_peak = 0.0
    min_observed_peak = 1.0e+99
    max_observed_peak = 0.0
    table_data = []
    table_color_dict = {}
    table_text_color_dict = {}
    #handles = []
    for model_category, group in df.groupby('Model Category'):
        min_predicted_peak = 1.0e+99
        max_predicted_peak = 0.0
        min_observed_peak = 1.0e+99
        max_observed_peak = 0.0
        onset_peak_group = group[['Predicted SEP Peak Intensity (Onset Peak)', 'Observed SEP Peak Intensity (Onset Peak)']].dropna()
        max_flux_group = group[['Predicted SEP Peak Intensity Max (Max Flux)', 'Observed SEP Peak Intensity Max (Max Flux)']].dropna()
        max_flux_in_prediction_window_group = group[['Predicted SEP Peak Intensity Max (Max Flux)', 'Observed Max Flux in Prediction Window']].dropna()
        is_onset_peak_empty = (filter_objects.is_column_empty(onset_peak_group, 'Predicted SEP Peak Intensity (Onset Peak)')) or (filter_objects.is_column_empty(onset_peak_group, 'Observed SEP Peak Intensity (Onset Peak)'))
        is_max_flux_empty = (filter_objects.is_column_empty(max_flux_group, 'Predicted SEP Peak Intensity Max (Max Flux)')) or (filter_objects.is_column_empty(max_flux_group, 'Observed SEP Peak Intensity Max (Max Flux)'))
        is_max_flux_in_prediction_window_empty = (filter_objects.is_column_empty(max_flux_in_prediction_window_group, 'Predicted SEP Peak Intensity Max (Max Flux)')) or (filter_objects.is_column_empty(max_flux_in_prediction_window_group, 'Observed Max Flux in Prediction Window'))
        if not plot_exists:
            if not is_onset_peak_empty:
                plot_exists = True
            elif not is_max_flux_empty:
                plot_exists = True
            elif not is_max_flux_in_prediction_window_empty:
                plot_exists = True
            else:
                continue

        if plot_exists:
            if (not figure_created):
                figure_created = True
                plt.figure(figsize=(config.image.peak_flux_width, config.image.peak_flux_height))
            if (not is_onset_peak_empty) or (not is_max_flux_empty) or (not is_max_flux_in_prediction_window_empty):
                #handles.append(matplotlib.patches.Patch(color=config.color.color_cycle[color_counter], label=model_category))
                if not is_onset_peak_empty:
                    this_group = onset_peak_group
                    data_type = 'Onset Peak'
                    prediction_column = 'Predicted SEP Peak Intensity (Onset Peak)'
                    observation_column = 'Observed SEP Peak Intensity (Onset Peak)'
                    min_predicted_peak = min(min_predicted_peak, this_group[this_group[prediction_column] > 0][prediction_column].min())
                    max_predicted_peak = max(max_predicted_peak, this_group[prediction_column].max())
                    min_observed_peak = min(min_observed_peak, this_group[this_group[observation_column] > 0][observation_column].min())
                    max_observed_peak = max(max_observed_peak, this_group[observation_column].max())
                    plt.scatter(this_group[observation_column], this_group[prediction_column], s=config.plot.marker_size, color=config.color.color_cycle[color_counter], marker=config.shape.associations[data_type], facecolors='none', zorder=2)
                    row, row_color_dict, row_text_color_dict = build_table_row(this_group, model_category, data_type, prediction_column, observation_column, threshold_flux, row_counter, color_counter) 
                    row_counter += 1
                    table_data.append(row)
                    table_color_dict.update(row_color_dict)
                    table_text_color_dict.update(row_text_color_dict)
                if not is_max_flux_empty:
                    this_group = max_flux_group
                    data_type = 'Max Flux'
                    prediction_column = 'Predicted SEP Peak Intensity Max (Max Flux)'
                    observation_column = 'Observed SEP Peak Intensity Max (Max Flux)'
                    min_predicted_peak = min(min_predicted_peak, this_group[this_group[prediction_column] > 0][prediction_column].min())
                    max_predicted_peak = max(max_predicted_peak, this_group[prediction_column].max())
                    min_observed_peak = min(min_observed_peak, this_group[this_group[observation_column] > 0][observation_column].min())
                    max_observed_peak = max(max_observed_peak, this_group[observation_column].max())
                    plt.scatter(this_group[observation_column], this_group[prediction_column], s=config.plot.marker_size, color=config.color.color_cycle[color_counter], marker=config.shape.associations[data_type], facecolors='none', zorder=1)
                    row, row_color_dict, row_text_color_dict = build_table_row(this_group, model_category, data_type, prediction_column, observation_column, threshold_flux, row_counter, color_counter)
                    row_counter += 1
                    table_data.append(row)
                    table_color_dict.update(row_color_dict)
                    table_text_color_dict.update(row_text_color_dict)
                if not is_max_flux_in_prediction_window_empty: 
                    this_group = max_flux_in_prediction_window_group
                    data_type = 'Max Flux in Prediction Window'
                    prediction_column = 'Predicted SEP Peak Intensity Max (Max Flux)'
                    observation_column = 'Observed Max Flux in Prediction Window' 
                    min_predicted_peak = min(min_predicted_peak, this_group[this_group[prediction_column] > 0][prediction_column].min())
                    max_predicted_peak = max(max_predicted_peak, this_group[prediction_column].max())
                    min_observed_peak = min(min_observed_peak, this_group[this_group[observation_column] > 0][observation_column].min())
                    max_observed_peak = max(max_observed_peak, this_group[observation_column].max())
                    plt.scatter(this_group[observation_column], this_group[prediction_column], s=config.plot.marker_size, color=config.color.color_cycle[color_counter], marker=config.shape.associations[data_type], facecolors='none', zorder=0)
                    row, row_color_dict, row_text_color_dict = build_table_row(this_group, model_category, data_type, prediction_column, observation_column, threshold_flux, row_counter, color_counter)
                    row_counter += 1
                    table_data.append(row)
                    table_color_dict.update(row_color_dict)
                    table_text_color_dict.update(row_text_color_dict)
                color_counter += 1

    if plot_exists:
        min_predicted_peak = min_predicted_peak / 2
        min_observed_peak = min_observed_peak / 2
        max_predicted_peak = max_predicted_peak * 2
        max_observed_peak = max_observed_peak * 2
        min_peak = min(min_predicted_peak, min_observed_peak)
        max_peak = max(max_predicted_peak, max_observed_peak)
       
        min_peak = min(min_peak, threshold_flux / 10)
        max_peak = max(max_peak, threshold_flux * 10)
 
        plt.plot([min_peak, max_peak], [min_peak, max_peak], color='black', linestyle='--')
        title = energy_channel_string + ', ' + threshold_flux_string
        color_key = title.replace('> ', '>=') + ' Event'
        plt.plot([threshold_flux, threshold_flux], [min_peak, max_peak], color=config.color.associations[color_key], linestyle='solid')
        plt.plot([min_peak, max_peak], [threshold_flux, threshold_flux], color=config.color.associations[color_key], linestyle='solid')
        #plt.grid()

        plt.title(title)
        plt.xlabel('Observed Peak Flux [pfu]')
        plt.ylabel('Predicted Peak Flux [pfu]')
        plt.xscale('log')
        plt.yscale('log')
        plt.xlim([min_peak, max_peak])
        plt.ylim([min_peak, max_peak])
        #plt.legend(handles=handles, loc='lower right', bbox_to_anchor=(1.0, 1.05), framealpha=config.plot.opacity, fontsize='small')
        plt.tight_layout()
        plt.savefig(save, dpi=config.image.dpi, bbox_inches=0)
        plt.close()
        return plot_exists, table_data, table_color_dict, table_text_color_dict
    else:
        return False, None, None, None

def build_table_row(df, model_category, data_type, prediction_column, observation_column, threshold_flux, row_counter=0, color_counter=0):
    hits_condition =              (df[prediction_column] >= threshold_flux) & (df[observation_column] >= threshold_flux)
    misses_condition =            (df[prediction_column] <  threshold_flux) & (df[observation_column] >= threshold_flux)
    false_alarms_condition =      (df[prediction_column] >= threshold_flux) & (df[observation_column] <  threshold_flux)
    correct_negatives_condition = (df[prediction_column] <  threshold_flux) & (df[observation_column] <  threshold_flux)
    hits =              str(len(df[hits_condition]))
    misses =            str(len(df[misses_condition]))
    false_alarms =      str(len(df[false_alarms_condition]))
    correct_negatives = str(len(df[correct_negatives_condition]))
    forecasts = str(len(df))
    row = [data_type, model_category, hits, misses, false_alarms, correct_negatives, forecasts]
    row_color_dict = {}
    row_text_color_dict = {}
    row_color_dict[(row_counter, 1)] = config.color.color_cycle[color_counter]
    row_color_dict[(row_counter, 2)] = config.color.associations['Hits']
    row_color_dict[(row_counter, 3)] = config.color.associations['Misses']
    row_color_dict[(row_counter, 4)] = config.color.associations['False Alarms']
    row_color_dict[(row_counter, 5)] = config.color.associations['Correct Negatives']
    row_text_color_dict[(row_counter, 1)] = '#ffffff'
    row_text_color_dict[(row_counter, 2)] = '#ffffff'
    row_text_color_dict[(row_counter, 3)] = '#ffffff'
    row_text_color_dict[(row_counter, 4)] = '#ffffff'
    row_text_color_dict[(row_counter, 5)] = '#ffffff'
    return row, row_color_dict, row_text_color_dict



