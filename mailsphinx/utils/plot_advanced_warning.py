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

def make_advanced_warning_time_axis(ax, sep_onset): 
    ax2 = ax.twiny()
    ax2.set_xlim(ax.get_xlim())
    ax2.set_xlabel('Advanced Warning Time [hours]')
    # MAKE SECONDARY LABELS
    # START WITH EVENT ONSET
    date_range = ax.get_xlim() # DAYS SINCE 1970-01-01 00:00:00 UTC
    ticks_before = []
    labels_before = []
    current_label = 0
    current_date = sep_onset.timestamp() / 60 / 60 / 24 # DAYS SINCE 1970-01-01 00:00:00 UTC
    while current_date > date_range[0]:
        current_date -= 1 / 24
        current_label += 1
        ticks_before.append(current_date)
        labels_before.append(current_label)
    ticks_after = []
    labels_after = []
    current_date = sep_onset.timestamp() / 60 / 60 / 24
    current_label = 0
    while current_date < date_range[1]:
        current_date += 1 / 24
        current_label -= 1
        ticks_after.append(current_date)
        labels_after.append(current_label)
    ticks_days = ticks_before + [sep_onset.timestamp() / 60 / 60 / 24] + ticks_after
    ticks = []
    for tick in ticks_days:
        ticks.append(datetime.datetime(year=1970, month=1, day=1, tzinfo=pytz.UTC) + datetime.timedelta(days=tick))
    ticklabels_int = labels_before + [0] + labels_after
    ticklabels = []
    for ticklabel in ticklabels_int:
        ticklabels.append(str(ticklabel))
    ax2.set_xticks(ticks)
    ax2.set_xticklabels(ticklabels)




def plot_advanced_warning(df, save, title, start_datetime, end_datetime, event):
    fig, ax = plt.subplots(figsize=(config.image.width, config.image.height))
    sep_onset = event['Observed SEP Threshold Crossing Time'].iloc[0]
    sep_end = event['Observed SEP End Time'].iloc[0]
    sep_onset_hour = 0
    sep_end_hour = (sep_end - sep_onset).total_seconds() / 60 / 60
    ax.set_title(title)
    for model_category, group in df.groupby('Model Category'):
        for model_flavor, subgroup in group.groupby('Model Flavor'):
            hit_condition = (subgroup['Predicted SEP All Clear'] == False) & (subgroup['Observed SEP All Clear'] == False)
            advanced_warning_times = sep_onset_hour - subgroup[hit_condition]['Forecast Issue Time'].dropna().dt.hour
            model = model_category + ' ' + model_flavor
            ax.scatter(advanced_warning_times, [model] * len(advanced_warning_times), color=config.color.associations['Hits'], marker=config.shape.contingency, s=config.plot.marker_size, facecolor='none')
    ax.axvspan(sep_onset_hour, sep_end_hour, color=config.color.associations[event['Energy'].iloc[0]], alpha=config.plot.opacity)
    ax.set_xlabel('Advanced Warning Time [hours]')

    labels = ax.get_xticklabels()
    reversed_labels = [str(-int(label.get_text().replace('\u2212', '-'))).replace('-', '\u2212') for label in labels]
    ax.set_xticklabels(reversed_labels)

    plt.tight_layout()
    plt.savefig(save, dpi=config.image.dpi)
    plt.close()


'''
def plot_advanced_warning(df, save, title, start_datetime, end_datetime, event):
    fig, ax = plt.subplots(figsize=(config.image.width, config.image.height))
    min_time = df['Forecast Issue Time'].min()
    sep_onset = event['Observed SEP Threshold Crossing Time'].iloc[0]
    sep_end = event['Observed SEP End Time'].iloc[0]
    ax.set_title(title)
    for model_category, group in df.groupby('Model Category'):
        for model_flavor, subgroup in group.groupby('Model Flavor'):
            hit_condition = (subgroup['Predicted SEP All Clear'] == False) & (subgroup['Observed SEP All Clear'] == False)
            forecast_issue_times = subgroup[hit_condition]['Forecast Issue Time'].dropna()
            model = model_category + ' ' + model_flavor
            ax.scatter(forecast_issue_times, [model] * len(forecast_issue_times), color=config.color.associations['Hits'], marker=config.shape.contingency, s=config.plot.marker_size, facecolor='none')
    ax.axvspan(sep_onset, sep_end, color=config.color.associations[event['Energy'].iloc[0]], alpha=config.plot.opacity)
    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%m-%d %H:%M'))
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
    make_advanced_warning_time_axis(ax, sep_onset)
    plt.tight_layout()
    plt.savefig(save, dpi=config.image.dpi)
    plt.close()
'''

def build_advanced_warning_plot(title, subgroup, save, start_datetime, end_datetime, event, convert_image_to_base64=False):
    plot_advanced_warning(subgroup, save, title, start_datetime, end_datetime, event)
    text = build_html.build_image(save, image_width_percentage=99, write_as_base64=convert_image_to_base64)
    return text

