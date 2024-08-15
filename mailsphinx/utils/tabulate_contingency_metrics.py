from ..utils import format_objects
from ..utils import build_html
from ..utils import config

import numpy as np

def build_single_stat_contingency_table(df, mode, header):
    if mode == 'hit':
        observed_sep_all_clear = False
        predicted_sep_all_clear = False
        stats = 'Hits'
    elif mode == 'miss':
        observed_sep_all_clear = False
        predicted_sep_all_clear = True
        stats = 'Misses'
    elif mode == 'false alarm':
        observed_sep_all_clear = True
        predicted_sep_all_clear = False
        stats = 'False Alarms'
    elif mode == 'correct negative':
        observed_sep_all_clear = True
        predicted_sep_all_clear = True
        stats = 'Correct Negatives'
    color = config.color.associations[stats]
    condition = (df['Observed SEP All Clear'] == observed_sep_all_clear) & (df['Predicted SEP All Clear'] == predicted_sep_all_clear)
    df_stat = df[condition]
    table_data = []
    df_stat = df_stat.applymap(format_objects.format_df_datetime)
    for index, row in df_stat.iterrows():
        table_row = row[header].apply(str).tolist()
        table_data.append(table_row)
    text = build_html.build_regular_text(stats + ': ' + str(len(df_stat)))
    if len(df_stat) > 0:
        text += build_html.build_table(header, table_data, header_color=color)
    return text

def compute_contingency_table_metrics(df, mode='all', additional_condition=True):
    hits = misses = false_alarms = correct_negatives = None
    if mode in ['all', 'hit']:
        hit_condition = (df['Observed SEP All Clear'] == False) & (df['Predicted SEP All Clear'] == False) & additional_condition
        hits = np.sum(hit_condition)
    if mode in ['all', 'miss']:
        miss_condition = (df['Observed SEP All Clear'] == False) & (df['Predicted SEP All Clear'] == True) & additional_condition
        misses = np.sum(miss_condition)
    if mode in ['all', 'false alarm']:
        false_alarm_condition = (df['Observed SEP All Clear'] == True) & (df['Predicted SEP All Clear'] == False) & additional_condition
        false_alarms = np.sum(false_alarm_condition)
    if mode in ['all', 'correct negative']:
        correct_negative_condition = (df['Observed SEP All Clear'] == True) & (df['Predicted SEP All Clear'] == True) & additional_condition
        correct_negatives = np.sum(correct_negative_condition)
    if additional_condition is True:
        forecasts = len(df)
    else:
        forecasts = np.sum(additional_condition)
    contingency_data = {'Hits' : hits,
                        'Misses' : misses,
                        'False Alarms' : false_alarms,
                        'Correct Negatives' : correct_negatives,
                        'Forecasts': forecasts}
    return contingency_data



def build_contingency_table_data(df, header, mode='all', parenthesized_start_datetime=None, parenthesized_end_datetime=None):
    table_data = []
    for name, group in df.groupby('Model Category'):
        for subname, subgroup in group.groupby('Model Flavor'):
            table_line_dict = dict(zip(header, [''] * len(header)))
            table_line_dict['Model Category'] = name
            table_line_dict['Model Flavor'] = subname
            table_line_dict['All-Time Report Link'] = build_html.build_html_shortlink('https://www.youtube.com/watch?v=xvFZjo5PgG0', name + ' ' + subname)
            contingency_data = compute_contingency_table_metrics(subgroup, mode=mode)
            if (parenthesized_start_datetime is not None) and (parenthesized_end_datetime is not None):
                parenthesized_condition = (subgroup['Forecast Issue Time'] < parenthesized_end_datetime) * (subgroup['Forecast Issue Time'] >= parenthesized_start_datetime)
                contingency_data_parenthesized = compute_contingency_table_metrics(subgroup, mode=mode, additional_condition=parenthesized_condition)
            else:
                contingency_data_parenthesized = None
            for item in header:
                if item in list(contingency_data.keys()):
                    if contingency_data[item] is not None:
                        if (contingency_data_parenthesized is not None):
                            table_line_dict[item] = format_objects.format_parenthesized_entry(contingency_data[item], contingency_data_parenthesized[item])
                        else:
                            table_line_dict[item] = str(contingency_data[item])
            table_data.append(list(table_line_dict.values()))
    return table_data


def build_all_clear_contingency_table(df, week_start, week_end):
    text = build_html.build_paragraph_title('All Clear Contingency Table')
    headers = ['Model Category', 'Model Flavor', 'Hits', 'Misses', 'False Alarms', 'Correct Negatives', 'Forecasts', 'All-Time Report Link']
    header_color_dict = dict(zip(headers, [None, None, config.color.associations['Hits'], config.color.associations['Misses'], config.color.associations['False Alarms'], config.color.associations['Correct Negatives'], None, None]))
    table_data = build_contingency_table_data(df, headers, 'all', week_start, week_end)
    text += build_html.build_table(headers, table_data, header_color_dict=header_color_dict)
    return text

def build_false_alarm_table(df):
    text = build_html.build_paragraph_title('False Alarms')
    headers = ['Model Category', 'Model Flavor', 'Forecast Issue Time', 'Prediction Window Start', 'Prediction Window End']
    text += build_single_stat_contingency_table(df, mode='false alarm', header=headers)
    return text

