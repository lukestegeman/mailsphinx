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


def _norm_energy_key(key):
    """Strip REleASE mismatch suffix for channel comparison."""
    return key.split('_min.')[0]


def _is_configured_channel(energy_key, threshold_key):
    """Return True if this (energy, threshold) pair is in the configured list."""
    norm = _norm_energy_key(energy_key)
    return any(norm == ek and threshold_key == tk
               for ek, tk, _ in config.order.energy_channel_threshold_order)


def _configured_thresholds_for_energy_key(energy_key):
    """Return every threshold_key configured for this (normalized) energy
    channel, per config.order.energy_channel_threshold_order."""
    norm = _norm_energy_key(energy_key)
    return [tk for ek, tk, _ in config.order.energy_channel_threshold_order if ek == norm]


def _section_heading_label(energy_key):
    """Build the section heading label for an energy channel, including
    the threshold when there's exactly one configured threshold for it
    (the common case), so headings read "> 10 MeV, > 10 pfu" instead of
    just "> 10 MeV" -- consistent with how every other section (Overview,
    Contingency Tables, Metrics Summary) labels channels. If more than
    one threshold is configured for the same energy channel, falls back
    to the energy-only label, since a single threshold can no longer
    unambiguously represent the whole heading."""
    energy_channel_string = manipulate_keys.convert_energy_key_to_string(energy_key)
    thresholds = _configured_thresholds_for_energy_key(energy_key)
    if len(thresholds) == 1:
        threshold_string = manipulate_keys.convert_threshold_key_to_string(thresholds[0])
        return f'{energy_channel_string}, {threshold_string}'
    return energy_channel_string


def build_model_section(df, weekly_df, week_start, week_end, events, convert_images_to_base64=False):
    text = build_html.build_section_title('Model Performance Time Series')

    # MAKE CONTINGENCY TIMELINES
    text += build_html.build_paragraph_title('SEP All Clear Contingency Timelines')
    counter = 0
    for energy_key, energy_group in weekly_df.groupby('Energy Channel Key'):
        # SKIP THIS ENERGY CHANNEL ENTIRELY IF NONE OF ITS THRESHOLD KEYS
        # ARE IN THE CONFIGURED LIST — AVOIDS RENDERING AN EMPTY HEADING.
        if not any(_is_configured_channel(energy_key, tk)
                   for tk in energy_group['Threshold Key'].unique()):
            continue
        energy_channel_string = _section_heading_label(energy_key)
        if energy_group['Energy Channel Key'].eq(energy_key).any():
            text += build_html.build_paragraph_title(energy_channel_string, sublevel=1)
            for model_category, group in energy_group.groupby('Model Category'):
                for model_flavor, subgroup in group.groupby('Model Flavor'):
                    for threshold_key, subsubgroup in subgroup.groupby('Threshold Key'):
                        if not _is_configured_channel(energy_key, threshold_key):
                            continue
                        filtered_events = events[(events['Energy Channel Key'] == energy_key) & (events['Threshold Key'] == threshold_key)]
                        threshold_string = manipulate_keys.convert_threshold_key_to_string(threshold_key)
                        if model_flavor == '':
                            space = ''
                        else:
                            space = ' '
                        title = model_category + space + model_flavor.replace('_', ' ') + ', ' + manipulate_keys.convert_energy_key_to_string(energy_key) + ', ' + threshold_string
                        text += plot_contingency.build_contingency_plot(title, subsubgroup, os.path.join(config.path.email_image, 'contingency-' + str(counter) + '.jpg'), week_start, week_end, filtered_events, convert_image_to_base64=convert_images_to_base64)
                        counter += 1

    # MAKE ADVANCED WARNING TIMELINES
    if len(events) > 0:
        counter = 0
        text += build_html.build_paragraph_title('Advanced Warning Time Comparison')
        for energy_key, energy_group in weekly_df.groupby('Energy Channel Key'):
            if not any(_is_configured_channel(energy_key, tk)
                       for tk in energy_group['Threshold Key'].unique()):
                continue
            energy_channel_string = _section_heading_label(energy_key)
            if energy_group['Energy Channel Key'].eq(energy_key).any():
                energy_reached = True
                for threshold_key, group in energy_group.groupby('Threshold Key'):
                    if not _is_configured_channel(energy_key, threshold_key):
                        continue
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
        if not any(_is_configured_channel(energy_key, tk)
                   for tk in energy_group['Threshold Key'].unique()):
            continue
        energy_channel_string = _section_heading_label(energy_key)
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
                    text += plot_probability.build_probability_plot(name + subname + ', ' + manipulate_keys.convert_energy_key_to_string(energy_key), group, os.path.join(config.path.email_image, 'probability-histogram-' + str(counter) + '.jpg'), week_start, week_end, filtered_events, need_legend=need_legend, convert_image_to_base64=convert_images_to_base64)
                    counter += 1

    # MAKE PREDICTED PEAK FLUX VS. OBSERVED PEAK FLUX — 4 PLOTS PER CHANNEL:
    # ALL-TIME ONSET PEAK, ALL-TIME MAX FLUX, THIS PERIOD ONSET PEAK,
    # THIS PERIOD MAX FLUX. KEEPS ALL-TIME AND CURRENT PERIOD VISUALLY SEPARATE.
    # ITERATE OVER CONFIGURED CHANNELS FROM df (NOT weekly_df) SO THAT MODELS
    # WITH NO FORECASTS IN THE CURRENT PERIOD STILL APPEAR IN ALL-TIME PLOTS.
    counter = 0
    section_started = False
    for energy_key, threshold_key, (axis_min, axis_max) in config.order.energy_channel_threshold_order:
        energy_channel_string = manipulate_keys.convert_energy_key_to_string(energy_key)
        threshold_flux_string = manipulate_keys.convert_threshold_key_to_string(threshold_key)
        threshold_flux = float(threshold_flux_string.lstrip('> ').rstrip(' pfu'))

        # NORMALIZE ENERGY KEY SO REleASE MISMATCH ROWS ARE INCLUDED
        all_time_mask = (
            df['Energy Channel Key'].apply(_norm_energy_key).eq(energy_key) &
            (df['Threshold Key'] == threshold_key)
        )
        period_mask = (
            weekly_df['Energy Channel Key'].apply(_norm_energy_key).eq(energy_key) &
            (weekly_df['Threshold Key'] == threshold_key)
        )
        all_time_subgroup = df[all_time_mask]
        period_subgroup = weekly_df[period_mask]

        channel_plots = []
        for source_df, period_label in [
            (all_time_subgroup, 'All Time'),
            (period_subgroup,   'This Period'),
        ]:
            for data_type_def in [plot_peak_flux.ONSET_PEAK, plot_peak_flux.MAX_FLUX]:
                plot_path = os.path.join(
                    config.path.email_image,
                    f'predicted-peak-flux-vs-observed-peak-flux-{counter}.jpg')
                counter += 1
                plot_exists, plot_text = plot_peak_flux.plot_peak_flux_single(
                    energy_channel_string, threshold_flux_string,
                    source_df, plot_path, threshold_flux,
                    data_type_def, period_label,
                    axis_min=axis_min, axis_max=axis_max,
                    convert_image_to_base64=convert_images_to_base64)
                if plot_exists:
                    channel_plots.append(plot_text)

        if not section_started:
            section_started = True
            text += build_html.build_paragraph_title(
                'Predicted Peak Flux vs. Observed Peak Flux')
        text += build_html.build_paragraph_title(
            f'{energy_channel_string}, {threshold_flux_string}', sublevel=1)
        for plot_text in channel_plots:
            text += plot_text
        # SINGLE SHARED LEGEND FOR ALL 4 PLOTS IN THIS CHANNEL
        legend_path = os.path.join(
            config.path.email_image,
            f'peak-flux-legend-{counter}.jpg')
        counter += 1
        text += plot_peak_flux.build_peak_flux_legend(
            df, legend_path,
            convert_image_to_base64=convert_images_to_base64)
    text += build_html.build_divider()
    return text
