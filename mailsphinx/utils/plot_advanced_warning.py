from ..utils import build_html
from ..utils import config

import datetime
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import pytz

plt.rcParams['font.family'] = config.plot.font
plt.rcParams['font.size'] = config.plot.fontsize
plt.rcParams['axes.prop_cycle'] = plt.cycler(color=config.color.color_cycle)

def plot_advanced_warning(df, save, title, start_datetime, end_datetime, event):
    unix_epoch = pd.Timestamp('1970-01-01 00:00:00+00:00')
    models = df['Model'].unique()
    fig, ax = plt.subplots(figsize=(config.image.width, config.image.vertical_category_allotment_advanced_warning * len(models) + config.image.advanced_warning_base_height))
    sep_onset = event['Observed SEP Threshold Crossing Time'].iloc[0]
    sep_end = event['Observed SEP End Time'].iloc[0]
    sep_onset_hour = (sep_onset - unix_epoch) / pd.Timedelta(hours=1)
    sep_duration_hour = (sep_end - sep_onset).total_seconds() / 60 / 60
    ax.set_title(title)
    for model_category, group in df.groupby('Model Category'):
        for model_flavor, subgroup in group.groupby('Model Flavor'):
            hit_condition = (subgroup['Predicted SEP All Clear'] == False) & (subgroup['Observed SEP All Clear'] == False)
            advanced_warning_times = sep_onset_hour - (subgroup[hit_condition]['Forecast Issue Time'].dropna() - unix_epoch) / pd.Timedelta(hours=1)
            model = model_category + ' ' + model_flavor
            ax.scatter(-advanced_warning_times, [model] * len(advanced_warning_times), color=config.color.associations['Hits'], marker=config.shape.contingency, s=config.plot.marker_size, facecolor='none')
    ax.axvspan(0, sep_duration_hour, color=config.color.associations[event['Energy'].iloc[0]], alpha=config.plot.opacity)
    ax.set_xlabel('Advanced Warning Time [hours]')

    labels = ax.get_xticklabels()
    reversed_labels = [str(-int(label.get_text().replace('\u2212', '-'))).replace('-', '\u2212') for label in labels]
    ax.set_xticklabels(reversed_labels)

    padding = 0.5
    ymin = 0
    ymax = len(models) - 1 - padding
    extended_min = ymin - padding
    extended_max = ymax
    ax.set_ylim(extended_min, extended_max)

    plt.tight_layout()
    plt.savefig(save, dpi=config.image.dpi)
    plt.close()

def build_advanced_warning_plot(title, subgroup, save, start_datetime, end_datetime, event, convert_image_to_base64=False):
    plot_advanced_warning(subgroup, save, title, start_datetime, end_datetime, event)
    text = build_html.build_image(save, image_width_percentage=99, write_as_base64=convert_image_to_base64)
    return text

