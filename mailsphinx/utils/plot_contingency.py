from ..utils import build_html
from ..utils import config

import datetime
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
plt.rcParams['font.family'] = config.plot.font
plt.rcParams['font.size'] = config.plot.fontsize
plt.rcParams['axes.prop_cycle'] = plt.cycler(color=config.color.color_cycle)


def get_contingency_df_dict(df):
    hit_condition =              (df['Observed SEP All Clear'] == False) & (df['Predicted SEP All Clear'] == False) & (df['All Clear Match Status'] == 'SEP Event')
    miss_condition =             (df['Observed SEP All Clear'] == False) & (df['Predicted SEP All Clear'] == True ) & (df['All Clear Match Status'] == 'SEP Event')
    false_alarm_condition =      (df['Observed SEP All Clear'] == True ) & (df['Predicted SEP All Clear'] == False) & (df['All Clear Match Status'] == 'No SEP Event')
    correct_negative_condition = (df['Observed SEP All Clear'] == True ) & (df['Predicted SEP All Clear'] == True ) & (df['All Clear Match Status'] == 'No SEP Event')
    invalid_condition = ~(hit_condition | miss_condition | false_alarm_condition | correct_negative_condition)

    hit_df = df[hit_condition]
    miss_df = df[miss_condition]
    false_alarm_df = df[false_alarm_condition]
    correct_negative_df = df[correct_negative_condition]
    invalid_df = df[invalid_condition]    

    df_dict = {'Hits' : hit_df,
               'Misses' : miss_df,
               'False Alarms' : false_alarm_df,
               'Correct Negatives' : correct_negative_df,
               'Invalid': invalid_df}
    return df_dict

def build_contingency_plot(title, subgroup, save, start_datetime, end_datetime):
    plot_contingency_table(subgroup, save, title, start_datetime, end_datetime)
    text = build_html.build_image(save, image_width_percentage=99)
    return text

def plot_contingency_table(df, save, title, start_datetime, end_datetime):
    df_dict = get_contingency_df_dict(df)
    reversed_categories = list(reversed(list(config.index.contingency.keys())))
    fig, ax = plt.subplots(figsize=(config.image.width, config.image.height))
    max_date = datetime.datetime.min
    count_position = end_datetime + pd.DateOffset(hours=12)
    for key, value in df_dict.items():

        if key == 'Invalid':
            for all_clear_match_status, group in df_dict[key].groupby('All Clear Match Status'):
                times = group['Prediction Window Start']
                ax.scatter(times, [config.index.contingency[key]] * len(times), color=config.color.associations[key], marker=config.shape.associations[all_clear_match_status], s=config.plot.marker_size, facecolor='none')
        else:
            times = df_dict[key]['Prediction Window Start']
            ax.scatter(times, [config.index.contingency[key]] * len(times), color=config.color.associations[key], marker=config.shape.contingency, s=config.plot.marker_size, facecolor='none')
        ax.text(count_position, config.index.contingency[key], len(df_dict[key]), fontsize=config.plot.fontsize, verticalalignment='center')
    ax.set_xlabel('UTC')
    ax.set_xlim([start_datetime, end_datetime])
    ax.set_yticks(range(len(reversed_categories)))
    ax.set_yticklabels(reversed_categories)
    ax.set_ylim([-0.2, 4.2])
    ax.set_title(title)
    ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y-%m-%d'))
    fig.autofmt_xdate()
    for tick in ax.get_xticks():
        ax.axvline(x=tick, color='gray', linewidth=0.5)
    plt.tight_layout()
    plt.subplots_adjust(left=config.html.left_padding_fraction)
    plt.savefig(save, dpi=config.image.dpi, bbox_inches=0)


    


    
        
    
    
