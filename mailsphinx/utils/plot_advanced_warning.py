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
    model_list = []
    advanced_warning_times_dict = {}
    fig, ax = plt.subplots(figsize=(config.image.width, config.image.vertical_category_allotment_advanced_warning * len(models) + config.image.advanced_warning_base_height))
    sep_onset = event['Observed SEP Threshold Crossing Time'].iloc[0]
    sep_duration_hour = event['Observed SEP Duration'].iloc[0]
    ax.set_title(title)
    for model_category, group in df.groupby('Model Category'):
        for model_flavor, subgroup in group.groupby('Model Flavor'):
            hit_condition = (subgroup['Predicted SEP All Clear'] == False) & (subgroup['Observed SEP All Clear'] == False) & (subgroup['Observed SEP Threshold Crossing Time'] == sep_onset)
            advanced_warning_times = (sep_onset - subgroup[hit_condition]['Forecast Issue Time'].dropna()) / pd.Timedelta(hours=1)
            model = model_category + ' ' + model_flavor
            model_list.append(model)
            advanced_warning_times_dict[model] = advanced_warning_times
            ax.scatter(-advanced_warning_times, [model] * len(advanced_warning_times), color=config.color.associations['Hits'], marker=config.shape.contingency, s=config.plot.marker_size, facecolor='none')
    ax.axvspan(0, sep_duration_hour, color=config.color.associations[event['Energy'].iloc[0]], alpha=config.plot.opacity)
    xmin, xmax = ax.get_xlim()
    for model in model_list:
        if (advanced_warning_times_dict[model] < -24).any():
            xmax = 24
            ax.scatter(xmax, model, color=config.color.associations['Misses'], marker='>')
        if (advanced_warning_times_dict[model] > 72).any():
            xmin = -72
            ax.scatter(xmin, model, color=config.color.associations['Misses'], marker='<')
    x_padding = (xmax - xmin) * 0.01
    ax.set_xlim(xmin - x_padding, xmax + x_padding)
    ax.set_xlabel('Advanced Warning Time [hours]')
    ax.tick_params(axis='y', pad=250)
    for label in ax.get_yticklabels():
        label.set_ha('left')
        label.set_x(0.0)    

    labels = ax.get_xticklabels()
    reversed_labels = []
    for label in labels:
        value = float(label.get_text().replace('\u2212', '-'))
        if (value > 0) and (value < 1):
            value = str(-value).replace('-', '\u2212')
        else:
            value = str(-int(value)).replace('-', '\u2212')
        reversed_labels.append(value)
    ax.set_xticklabels(reversed_labels)
    padding = 0.5
    ymin, ymax = ax.get_ylim()
    ymin -= padding
    ymax += padding
    ax.set_ylim(ymin, ymax)
    ax.grid(True, axis='x', color='gray', linewidth=0.5)
    plt.tight_layout()
    plt.savefig(save, dpi=config.image.dpi)
    plt.close()

def build_advanced_warning_plot(title, subgroup, save, start_datetime, end_datetime, event, convert_image_to_base64=False):
    plot_advanced_warning(subgroup, save, title, start_datetime, end_datetime, event)
    text = build_html.build_image(save, image_width_percentage=99, write_as_base64=convert_image_to_base64)
    return text

