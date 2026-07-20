from ..utils import build_html
from ..utils import config
from ..utils import filter_objects

import numpy as np
import matplotlib
import matplotlib.lines
import matplotlib.patches
import matplotlib.pyplot as plt

plt.rcParams['font.family'] = config.plot.font
plt.rcParams['font.size'] = config.plot.fontsize

def build_peak_flux_plot(energy_channel_string, threshold_flux_string, df, savefile, threshold_flux, all_time_df=None, convert_image_to_base64=False):
    plot_exists = plot_predicted_peak_flux_vs_observed_peak_flux(
        energy_channel_string, threshold_flux_string, df, savefile, threshold_flux,
        all_time_df=all_time_df)
    text = ''
    if plot_exists:
        text += build_html.build_image(savefile, write_as_base64=convert_image_to_base64)
    return plot_exists, text

def plot_predicted_peak_flux_vs_observed_peak_flux(energy_channel_string, threshold_flux_string, df, save, threshold_flux, all_time_df=None):
    """Plot predicted vs. observed peak flux.

    If config.peak_flux_scope == 'all_time' and all_time_df is provided,
    all-time points are plotted faded in the background and current period
    points are plotted prominently on top. Otherwise only current period
    points are shown.
    """
    use_all_time = (
        getattr(config, 'peak_flux_scope', 'current') == 'all_time'
        and all_time_df is not None
    )

    def _scatter_groups(source_df, alpha, marker_size_factor=1.0, zorder_offset=0):
        """Scatter onset peak and max flux points from source_df.
        Returns True if any data was plotted, and updates the shared bounds."""
        nonlocal min_predicted_peak, max_predicted_peak, min_observed_peak, max_observed_peak
        any_data = False
        for model_category, group in source_df.groupby('Model Category'):
            onset_peak_group = group[['Predicted SEP Peak Intensity (Onset Peak)', 'Observed SEP Peak Intensity (Onset Peak)']].dropna()
            max_flux_group = group[['Predicted SEP Peak Intensity Max (Max Flux)', 'Observed SEP Peak Intensity Max (Max Flux)']].dropna()
            is_onset_peak_empty = (filter_objects.is_column_empty(onset_peak_group, 'Predicted SEP Peak Intensity (Onset Peak)')) or (filter_objects.is_column_empty(onset_peak_group, 'Observed SEP Peak Intensity (Onset Peak)'))
            is_max_flux_empty = (filter_objects.is_column_empty(max_flux_group, 'Predicted SEP Peak Intensity Max (Max Flux)')) or (filter_objects.is_column_empty(max_flux_group, 'Observed SEP Peak Intensity Max (Max Flux)'))
            if is_onset_peak_empty and is_max_flux_empty:
                continue
            any_data = True
            color = config.color.color_cycle[list(source_df['Model Category'].unique()).index(model_category) % len(config.color.color_cycle)]
            if not is_onset_peak_empty:
                pred_col = 'Predicted SEP Peak Intensity (Onset Peak)'
                obs_col  = 'Observed SEP Peak Intensity (Onset Peak)'
                valid = onset_peak_group[(onset_peak_group[pred_col] > 0) & (onset_peak_group[obs_col] > 0)]
                if len(valid):
                    min_predicted_peak = min(min_predicted_peak, valid[pred_col].min())
                    max_predicted_peak = max(max_predicted_peak, valid[pred_col].max())
                    min_observed_peak  = min(min_observed_peak,  valid[obs_col].min())
                    max_observed_peak  = max(max_observed_peak,  valid[obs_col].max())
                plt.scatter(onset_peak_group[obs_col], onset_peak_group[pred_col],
                            s=config.plot.marker_size * marker_size_factor,
                            color=color, marker=config.shape.associations['Onset Peak'],
                            facecolors='none', alpha=alpha,
                            zorder=2 + zorder_offset)
            if not is_max_flux_empty:
                pred_col = 'Predicted SEP Peak Intensity Max (Max Flux)'
                obs_col  = 'Observed SEP Peak Intensity Max (Max Flux)'
                valid = max_flux_group[(max_flux_group[pred_col] > 0) & (max_flux_group[obs_col] > 0)]
                if len(valid):
                    min_predicted_peak = min(min_predicted_peak, valid[pred_col].min())
                    max_predicted_peak = max(max_predicted_peak, valid[pred_col].max())
                    min_observed_peak  = min(min_observed_peak,  valid[obs_col].min())
                    max_observed_peak  = max(max_observed_peak,  valid[obs_col].max())
                plt.scatter(max_flux_group[obs_col], max_flux_group[pred_col],
                            s=config.plot.marker_size * marker_size_factor,
                            color=color, marker=config.shape.associations['Max Flux'],
                            facecolors='none', alpha=alpha,
                            zorder=1 + zorder_offset)
        return any_data

    plot_exists = False
    figure_created = False
    min_predicted_peak = 1.0e+99
    max_predicted_peak = 0.0
    min_observed_peak  = 1.0e+99
    max_observed_peak  = 0.0
    handles = []

    # CHECK IF CURRENT PERIOD HAS ANY DATA BEFORE CREATING FIGURE
    has_onset = not (filter_objects.is_column_empty(df, 'Predicted SEP Peak Intensity (Onset Peak)') or
                     filter_objects.is_column_empty(df, 'Observed SEP Peak Intensity (Onset Peak)'))
    has_max   = not (filter_objects.is_column_empty(df, 'Predicted SEP Peak Intensity Max (Max Flux)') or
                     filter_objects.is_column_empty(df, 'Observed SEP Peak Intensity Max (Max Flux)'))
    if not has_onset and not has_max:
        return False

    # IF all_time MODE, ALSO CHECK ALL-TIME DATA
    if use_all_time:
        at_has_onset = not (filter_objects.is_column_empty(all_time_df, 'Predicted SEP Peak Intensity (Onset Peak)') or
                            filter_objects.is_column_empty(all_time_df, 'Observed SEP Peak Intensity (Onset Peak)'))
        at_has_max   = not (filter_objects.is_column_empty(all_time_df, 'Predicted SEP Peak Intensity Max (Max Flux)') or
                            filter_objects.is_column_empty(all_time_df, 'Observed SEP Peak Intensity Max (Max Flux)'))
        if not at_has_onset and not at_has_max:
            use_all_time = False

    plt.figure(figsize=(config.image.peak_flux_width, config.image.peak_flux_height))

    if use_all_time:
        # FADED ALL-TIME POINTS IN BACKGROUND
        _scatter_groups(all_time_df, alpha=0.15, marker_size_factor=0.8, zorder_offset=0)
        # PROMINENT CURRENT PERIOD POINTS ON TOP
        _scatter_groups(df, alpha=0.9, marker_size_factor=1.5, zorder_offset=10)
    else:
        _scatter_groups(df, alpha=0.85, marker_size_factor=1.0, zorder_offset=0)

    # BUILD LEGEND PER MODEL CATEGORY FROM CURRENT PERIOD
    for i, model_category in enumerate(sorted(df['Model Category'].unique())):
        color = config.color.color_cycle[i % len(config.color.color_cycle)]
        handles.append(matplotlib.patches.Patch(color=color, label=model_category))

    plot_exists = True

    import math
    if min_predicted_peak >= 1.0e+98 or min_observed_peak >= 1.0e+98:
        plt.close()
        return False

    log_thresh = math.log10(threshold_flux)
    axis_min = 10 ** (log_thresh - 3.0)
    axis_max = 10 ** (log_thresh + 4.0)  # ONE EXTRA DECADE ON THE UPPER-RIGHT

    plt.plot([axis_min, axis_max], [axis_min, axis_max],
             color='black', linestyle='--', zorder=0)
    title = energy_channel_string + ', ' + threshold_flux_string
    color_key = title.replace('> ', '>=') + ' Event'
    plt.plot([threshold_flux, threshold_flux], [axis_min, axis_max],
             color=config.color.associations[color_key], linestyle='solid', zorder=0)
    plt.plot([axis_min, axis_max], [threshold_flux, threshold_flux],
             color=config.color.associations[color_key], linestyle='solid', zorder=0)

    plt.grid(True, which='major', linestyle='--', linewidth=0.5, alpha=0.7)
    plt.title(title)
    plt.xlabel('Observed Peak Flux [pfu]')
    plt.ylabel('Predicted Peak Flux [pfu]')
    plt.xscale('log')
    plt.yscale('log')
    plt.xlim([axis_min, axis_max])
    plt.ylim([axis_min, axis_max])

    if use_all_time:
        handles += [
            matplotlib.lines.Line2D([0], [0], marker='o', color='gray',
                                    alpha=0.3, linestyle='None', markersize=5,
                                    label='All time'),
            matplotlib.lines.Line2D([0], [0], marker='o', color='gray',
                                    alpha=0.9, linestyle='None', markersize=7,
                                    label='This period'),
        ]

    if handles:
        # PLACE LEGEND OUTSIDE THE PLOT TO THE RIGHT SO IT DOESN'T
        # OVERLAP DATA AND THE PLOTTING AREA ASPECT RATIO IS UNCHANGED.
        plt.legend(handles=handles, loc='upper left',
                   bbox_to_anchor=(1.02, 1.0),
                   borderaxespad=0,
                   framealpha=config.plot.opacity,
                   fontsize='small')
    plt.tight_layout()
    plt.savefig(save, dpi=config.image.dpi, bbox_inches='tight')
    plt.close()
    return plot_exists

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
