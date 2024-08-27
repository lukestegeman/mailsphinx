from ..utils import build_html
from ..utils import config

import datetime
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

plt.rcParams['font.family'] = config.plot.font
plt.rcParams['font.size'] = config.plot.fontsize
plt.rcParams['axes.prop_cycle'] = plt.cycler(color=config.color.color_cycle)

def get_contingency_df_dict(df):
    hit_condition =              (df['Observed SEP All Clear'] == False) & (df['Predicted SEP All Clear'] == False)
    miss_condition =             (df['Observed SEP All Clear'] == False) & (df['Predicted SEP All Clear'] == True )
    false_alarm_condition =      (df['Observed SEP All Clear'] == True ) & (df['Predicted SEP All Clear'] == False)
    correct_negative_condition = (df['Observed SEP All Clear'] == True ) & (df['Predicted SEP All Clear'] == True )
    not_evaluated_condition = ~(hit_condition | miss_condition | false_alarm_condition | correct_negative_condition)

    hit_df = df[hit_condition]
    miss_df = df[miss_condition]
    false_alarm_df = df[false_alarm_condition]
    correct_negative_df = df[correct_negative_condition]
    not_evaluated_df = df[not_evaluated_condition]

    df_dict = {'Hits' : hit_df,
               'Misses' : miss_df,
               'False Alarms' : false_alarm_df,
               'Correct Negatives' : correct_negative_df,
               'Not Evaluated': not_evaluated_df}
    return df_dict

def build_contingency_plot(title, subgroup, save, start_datetime, end_datetime, events, convert_image_to_base64=False):
    plot_contingency_table(subgroup, save, title, start_datetime, end_datetime, events)
    text = build_html.build_image(save, image_width_percentage=99, write_as_base64=convert_image_to_base64)
    return text

def plot_contingency_table(df, save, title, start_datetime, end_datetime, events):
    df_dict = get_contingency_df_dict(df)
    reversed_categories = list(reversed(list(config.index.contingency.keys())))
    fig, ax = plt.subplots(figsize=(config.image.width, config.image.height_contingency))
    max_date = datetime.datetime.min
    count_position = end_datetime + pd.DateOffset(hours=12)
    for key, value in df_dict.items():

        if key == 'Not Evaluated':
            for all_clear_match_status, group in df_dict[key].groupby('All Clear Match Status'):
                times = group['Prediction Window Start']
                ax.scatter(times, [config.index.contingency[key]] * len(times), color=config.color.associations[key], marker=config.shape.associations[all_clear_match_status], s=config.plot.marker_size, facecolor='none')
        else:
            times = df_dict[key]['Prediction Window Start']
            ax.scatter(times, [config.index.contingency[key]] * len(times), color=config.color.associations[key], marker=config.shape.contingency, s=config.plot.marker_size, facecolor='none')
        ax.text(count_position, config.index.contingency[key], len(df_dict[key]), fontsize=config.plot.fontsize, verticalalignment='center', color=config.color.associations[key])

    for index, event in events.iterrows():
        ax.axvspan(event['Observed SEP Threshold Crossing Time'], event['Observed SEP End Time'], color=config.color.associations[event['Energy']], alpha=config.plot.opacity)
    ax.set_xlim([start_datetime, end_datetime])
    ax.set_yticks(range(len(reversed_categories)))
    ax.set_yticklabels(reversed_categories)
    ax.set_ylim([-0.2, 4.2])
    ax.set_title(title)

    xticks = pd.date_range(start_datetime, end_datetime)
    ax.set_xticks(xticks)
    counter = 0
    labels = []
    for date in ax.get_xticklabels():
        if counter == 0 or counter == len(ax.get_xticklabels()) - 1:
            label = date
        else:
            label = ''
        labels.append(label)
        counter += 1
    ax.set_xticklabels(labels)
    #ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y-%m-%d'))
    fig.autofmt_xdate(rotation=0, ha='center')
    for tick in ax.get_xticks():
        ax.axvline(x=tick, color='gray', linewidth=0.5)

    yticks = ax.get_yticks()
    ytick_labels = ax.get_yticklabels()
    for i, tick_label in enumerate(ytick_labels):
        tick_label.set_color(config.color.associations[tick_label.get_text()])


    plt.tight_layout()
    #fig.patch.set_facecolor('red')
    plt.subplots_adjust(left=config.html.left_padding_fraction, right=0.9)
    plt.savefig(save, dpi=config.image.dpi, bbox_inches=0)
    plt.close()

    


    
        
    
    
