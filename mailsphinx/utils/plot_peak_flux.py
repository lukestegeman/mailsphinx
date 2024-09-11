from ..utils import build_html
from ..utils import config
from ..utils import filter_objects

import numpy as np
import matplotlib
import matplotlib.pyplot as plt

plt.rcParams['font.family'] = config.plot.font
plt.rcParams['font.size'] = config.plot.fontsize

def build_peak_flux_plot(energy_channel_string, threshold_flux_string, df, savefile, threshold_flux, convert_image_to_base64=False):
    plot_exists = plot_predicted_peak_flux_vs_observed_peak_flux(energy_channel_string, threshold_flux_string, df, savefile, threshold_flux)
    text = ''
    if plot_exists:
        text = build_html.build_image(savefile, write_as_base64=convert_image_to_base64)
    return plot_exists, text

def plot_predicted_peak_flux_vs_observed_peak_flux(energy_channel_string, threshold_flux_string, df, save, threshold_flux):
    color_counter = 0
    plot_exists = False
    figure_created = False
    min_predicted_peak = 1.0e+99
    max_predicted_peak = 0.0
    min_observed_peak = 1.0e+99
    max_observed_peak = 0.0
    handles = []
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
        else:

            if (not figure_created):
                figure_created = True
                plt.figure(figsize=(config.image.peak_flux_width, config.image.peak_flux_height))
            if (not is_onset_peak_empty) or (not is_max_flux_empty) or (not is_max_flux_in_prediction_window_empty):
                handles.append(matplotlib.patches.Patch(color=config.color.color_cycle[color_counter], label=model_category))
                if not is_onset_peak_empty:
                    min_predicted_peak = min(min_predicted_peak, onset_peak_group['Predicted SEP Peak Intensity (Onset Peak)'].min())
                    max_predicted_peak = max(max_predicted_peak, onset_peak_group['Predicted SEP Peak Intensity (Onset Peak)'].max()) 
                    min_observed_peak = min(min_observed_peak, onset_peak_group['Observed SEP Peak Intensity (Onset Peak)'].min())
                    max_observed_peak = max(max_observed_peak, onset_peak_group['Observed SEP Peak Intensity (Onset Peak)'].max())
                    plt.scatter(onset_peak_group['Observed SEP Peak Intensity (Onset Peak)'], onset_peak_group['Predicted SEP Peak Intensity (Onset Peak)'], s=config.plot.marker_size, color=config.color.color_cycle[color_counter], marker=config.shape.associations['Onset Peak'], facecolors='none') 
                if not is_max_flux_empty:
                    plt.scatter(max_flux_group['Observed SEP Peak Intensity Max (Max Flux)'], max_flux_group['Predicted SEP Peak Intensity Max (Max Flux)'], s=config.plot.marker_size, color=config.color.color_cycle[color_counter], marker=config.shape.associations['Max Flux'])
                    min_predicted_peak = min(min_predicted_peak, max_flux_group['Predicted SEP Peak Intensity Max (Max Flux)'].min())
                    max_predicted_peak = max(max_predicted_peak, max_flux_group['Predicted SEP Peak Intensity Max (Max Flux)'].max()) 
                    min_observed_peak = min(min_observed_peak, max_flux_group['Observed SEP Peak Intensity Max (Max Flux)'].min())
                    max_observed_peak = max(max_observed_peak, max_flux_group['Observed SEP Peak Intensity Max (Max Flux)'].max())
                if not is_max_flux_in_prediction_window_empty: 
                    min_observed_peak = min(min_observed_peak, max_flux_in_prediction_window_group['Observed Max Flux in Prediction Window'].min())
                    max_observed_peak = max(max_observed_peak, max_flux_in_prediction_window_group['Observed Max Flux in Prediction Window'].max())
                    plt.scatter(max_flux_in_prediction_window_group['Observed Max Flux in Prediction Window'], max_flux_in_prediction_window_group['Predicted SEP Peak Intensity Max (Max Flux)'], s=config.plot.marker_size, color=config.color.color_cycle[color_counter], marker=config.shape.associations['Max Flux in Prediction Window']) 
                color_counter += 1
            
    if plot_exists:
        min_peak = min(min_predicted_peak, min_observed_peak)
        max_peak = max(max_predicted_peak, max_observed_peak)
        difference = np.log10(max_peak - min_peak)
        min_peak = min_peak / 2
        max_peak = max_peak * 2
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
        plt.legend(handles=handles, loc='lower right', bbox_to_anchor=(1.0, 1.05), framealpha=config.plot.opacity, fontsize='small')
        plt.tight_layout()
        plt.savefig(save, dpi=config.image.dpi, bbox_inches=0)
        plt.close()
    return plot_exists








