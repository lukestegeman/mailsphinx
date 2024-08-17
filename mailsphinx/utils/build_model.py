from ..utils import build_html
from ..utils import tabulate_contingency_metrics
from ..utils import plot_peak_flux
from ..utils import plot_probability
from ..utils import plot_contingency
from ..utils import filter_objects
from ..utils import manipulate_keys
from ..utils import config

import os

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

def build_model_section_new(df, weekly_df, week_start, week_end):
    text = build_html.build_section_title('Model Performance')

    # MAKE CONTINGENCY TIMELINES
    text += build_html.build_paragraph_title('SEP All Clear Contingency Timelines')
    counter = 0
    for model_category, group in weekly_df.groupby('Model Category'):
        for model_flavor, subgroup in group.groupby('Model Flavor'):
            for energy_key, subsubgroup in subgroup.groupby('Energy Channel Key'):
                energy_channel_string = manipulate_keys.convert_energy_key_to_string(energy_key)
                for threshold_key, subsubsubgroup in subsubgroup.groupby('Threshold Key'):
                    threshold_string = manipulate_keys.convert_threshold_key_to_string(threshold_key)
                    if model_flavor == '':
                        space = ''
                    else:
                        space = ' '
                    text += plot_contingency.build_contingency_plot(model_category + space + model_flavor.replace('_', ' ') + ', ' + energy_channel_string + ', ' + threshold_string, subsubsubgroup, os.path.join(config.path.email_image, 'contingency-' + str(counter) + '.jpg'), week_start, week_end)
                    counter += 1

    # MAKE PROBABILITY TIMELINES WITH VERTICAL HISTOGRAMS
    text += build_html.build_paragraph_title('SEP Probability Timelines')
    counter = 0
    for name, group in weekly_df.groupby('Model Category'):
        if not filter_objects.is_column_empty(group, 'Predicted SEP Probability'):
            text += plot_probability.build_probability_plot(name, group, os.path.join(config.path.email_image, 'probability-histogram-' + str(counter) + '.jpg'), week_start, week_end)
            counter += 1

    # MAKE PREDICTED PEAK FLUX VS. OBSERVED PEAK FLUX
    text += build_html.build_paragraph_title('Predicted Peak Flux vs. Observed Peak Flux')
    counter = 0
    for name, group in weekly_df.groupby('Energy Channel Key'):
        text += plot_peak_flux.build_peak_flux_plot(group, os.path.join(config.path.email_image, 'predicted-peak-flux-vs-observed-peak-flux-' + str(counter) + '.jpg'))
        counter += 1

    # MAKE CONTINGENCY TABLE
    text += tabulate_contingency_metrics.build_all_clear_contingency_table(df, week_start, week_end)

    text += build_html.build_divider()

    return text



