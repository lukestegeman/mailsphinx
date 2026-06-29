from ..utils import build_html
from ..utils import config
from ..utils import format_objects

import numpy as np
import os

# ABBREVIATED LABELS FOR NOT-EVALUATED MATCH STATUSES USED IN THE
# BREAKDOWN TABLE. FULL NAMES ARE SHOWN IN THE LEGEND ABOVE THE TABLE.
_NE_ABBREVIATIONS = {
    'Ongoing SEP Event':                        'OSE',
    'No SEP Event':                             'NSE',
    'Trigger not associated with observed SEP': 'TNS',
    'SEP Event':                                'SE',
    'No SEP Event (SubEvent)':                  'NSE-S',
    'Trigger/Input after Observed Phenomenon':  'TIA',
}


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


def _not_evaluated_condition(df):
    """Return a boolean Series for rows that fall outside the four
    standard contingency categories."""
    hit = (df['Observed SEP All Clear'] == False) & (df['Predicted SEP All Clear'] == False)
    miss = (df['Observed SEP All Clear'] == False) & (df['Predicted SEP All Clear'] == True)
    fa = (df['Observed SEP All Clear'] == True) & (df['Predicted SEP All Clear'] == False)
    cn = (df['Observed SEP All Clear'] == True) & (df['Predicted SEP All Clear'] == True)
    return ~(hit | miss | fa | cn)


def compute_contingency_table_metrics(df, mode='all', additional_condition=True):
    hits = misses = false_alarms = correct_negatives = not_evaluated = None
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
    if mode == 'all':
        ne_condition = _not_evaluated_condition(df) & additional_condition
        not_evaluated = np.sum(ne_condition)
    if additional_condition is True:
        forecasts = len(df)
    else:
        forecasts = np.sum(additional_condition)
    contingency_data = {
        'Hits':              hits,
        'Misses':            misses,
        'False Alarms':      false_alarms,
        'Correct Negatives': correct_negatives,
        'Not Evaluated':     not_evaluated,
        'Forecasts':         forecasts,
    }
    return contingency_data


def compute_ne_breakdown(df, additional_condition=True):
    """Return a dict mapping each abbreviated NE match status to its count."""
    ne_mask = _not_evaluated_condition(df)
    if additional_condition is not True:
        ne_mask = ne_mask & additional_condition
    ne_df = df[ne_mask]
    breakdown = {}
    for full_name, abbrev in _NE_ABBREVIATIONS.items():
        breakdown[abbrev] = (ne_df['All Clear Match Status'] == full_name).sum()
    return breakdown


def build_contingency_table_data(df, header, mode='all', parenthesized_start_datetime=None, parenthesized_end_datetime=None):
    table_data = []
    table_color_dict = {}
    table_text_color_dict = {}
    # BREAKDOWN TABLE DATA: ONE ROW PER MODEL/FLAVOR, COLUMNS ARE NE ABBREVS
    breakdown_table_data = []
    ne_abbrev_list = list(_NE_ABBREVIATIONS.values())

    row_counter = 0
    for name, group in df.groupby('Model Category'):
        for subname, subgroup in group.groupby('Model Flavor'):
            # MAIN TABLE ROW
            table_line_dict = dict(zip(header, [''] * len(header)))
            table_line_dict['Model Category'] = name
            table_line_dict['Model Flavor'] = subname
            table_line_dict['All-Time Report Link'] = build_html.build_html_shortlink(
                os.path.join(config.path.report, subgroup['Model'].iloc[0] + '_report.html'),
                name + ' ' + subname)
            contingency_data = compute_contingency_table_metrics(subgroup, mode=mode)
            if (parenthesized_start_datetime is not None) and (parenthesized_end_datetime is not None):
                parenthesized_condition = (
                    (subgroup['Forecast Issue Time'] < parenthesized_end_datetime) *
                    (subgroup['Forecast Issue Time'] >= parenthesized_start_datetime)
                )
                contingency_data_parenthesized = compute_contingency_table_metrics(
                    subgroup, mode=mode, additional_condition=parenthesized_condition)
            else:
                contingency_data_parenthesized = None
            for item in header:
                if item in list(contingency_data.keys()):
                    if contingency_data[item] is not None:
                        if contingency_data_parenthesized is not None:
                            table_line_dict[item] = format_objects.format_parenthesized_entry(
                                contingency_data[item], contingency_data_parenthesized[item])
                        else:
                            table_line_dict[item] = str(contingency_data[item])
            table_data.append(list(table_line_dict.values()))

            # COLOR CODING FOR MAIN TABLE
            color_map = {
                'Hits': 2, 'Misses': 3, 'False Alarms': 4,
                'Correct Negatives': 5,
            }
            for key, col_idx in color_map.items():
                table_color_dict[(row_counter, col_idx)] = config.color.associations[key]
                table_text_color_dict[(row_counter, col_idx)] = '#ffffff'

            # BREAKDOWN TABLE ROW
            breakdown_all = compute_ne_breakdown(subgroup)
            breakdown_row = [name, subname]
            if contingency_data_parenthesized is not None:
                breakdown_week = compute_ne_breakdown(subgroup, additional_condition=parenthesized_condition)
                for abbrev in ne_abbrev_list:
                    breakdown_row.append(format_objects.format_parenthesized_entry(
                        breakdown_all[abbrev], breakdown_week[abbrev]))
            else:
                for abbrev in ne_abbrev_list:
                    breakdown_row.append(str(breakdown_all[abbrev]))
            breakdown_table_data.append(breakdown_row)

            row_counter += 1
    return table_data, table_color_dict, table_text_color_dict, breakdown_table_data


def _build_ne_legend():
    """Build a small legend table mapping abbreviations to full match status names."""
    headers = ['Abbreviation', 'Match Status']
    table_data = [[abbrev, full] for full, abbrev in _NE_ABBREVIATIONS.items()]
    return build_html.build_table(headers, table_data)


def build_all_clear_contingency_table(df, week_start, week_end):
    text = build_html.build_paragraph_title('All Clear Contingency Tables')
    text += build_html.build_regular_text(
        "Values are given in the form X (+Y), where X is the all-time quantity, "
        "and Y is the quantity added from this week's results. X is inclusive of Y.")

    headers = ['Model Category', 'Model Flavor', 'Hits', 'Misses', 'False Alarms',
               'Correct Negatives', 'Not Evaluated', 'Forecasts', 'All-Time Report Link']
    header_color_dict = dict(zip(headers, [
        None, None,
        config.color.associations['Hits'],
        config.color.associations['Misses'],
        config.color.associations['False Alarms'],
        config.color.associations['Correct Negatives'],
        None, None, None,
    ]))

    table_data, table_color_dict, table_text_color_dict, breakdown_table_data = \
        build_contingency_table_data(df, headers, 'all', week_start, week_end)

    text += build_html.build_table(
        headers, table_data,
        header_color_dict=header_color_dict,
        table_color_dict=table_color_dict,
        table_text_color_dict=table_text_color_dict)

    # NOT-EVALUATED BREAKDOWN TABLE WITH LEGEND
    text += build_html.build_paragraph_title('Not Evaluated Breakdown')
    text += build_html.build_regular_text(
        "Counts of not-evaluated forecasts by match status reason. "
        "Values are in the form X (+Y) as above.")
    text += _build_ne_legend()
    ne_abbrev_list = list(_NE_ABBREVIATIONS.values())
    breakdown_headers = ['Model Category', 'Model Flavor'] + ne_abbrev_list
    text += build_html.build_table(breakdown_headers, breakdown_table_data)

    text += build_html.build_divider()
    return text


def build_false_alarm_table(df):
    text = build_html.build_paragraph_title('False Alarms')
    headers = ['Model Category', 'Model Flavor', 'Forecast Issue Time',
               'Prediction Window Start', 'Prediction Window End']
    text += build_single_stat_contingency_table(df, mode='false alarm', header=headers)
    return text
