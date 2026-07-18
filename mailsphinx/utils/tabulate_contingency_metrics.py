from ..utils import build_html
from ..utils import build_evaluation_breakdown as _eb
from ..utils import config
from ..utils import format_objects
from ..utils import manipulate_keys

import numpy as np
import os

# USE NE_ABBREVIATIONS FROM build_evaluation_breakdown — SINGLE SOURCE OF TRUTH
_NE_ABBREVIATIONS = _eb.NE_ABBREVIATIONS


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
    """Return a boolean Series for rows outside the four standard
    contingency categories."""
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
    return {
        'Hits':              hits,
        'Misses':            misses,
        'False Alarms':      false_alarms,
        'Correct Negatives': correct_negatives,
        'Not Evaluated':     not_evaluated,
        'Forecasts':         forecasts,
    }


def compute_ne_breakdown(df, additional_condition=True):
    """Return a dict mapping each abbreviated NE match status to its count."""
    ne_mask = _not_evaluated_condition(df)
    if additional_condition is not True:
        ne_mask = ne_mask & additional_condition
    ne_df = df[ne_mask]
    return {abbrev: (ne_df['All Clear Match Status'] == full_name).sum()
            for full_name, abbrev in _NE_ABBREVIATIONS.items()}


def _channel_label(energy_key, threshold_key):
    """Return a human-readable label for an energy/threshold pair."""
    energy_str = manipulate_keys.convert_energy_key_to_string(energy_key)
    threshold_str = manipulate_keys.convert_threshold_key_to_string(threshold_key)
    return f'{energy_str}, {threshold_str}'


def _normalize_energy_key(energy_key):
    """Strip the mismatch suffix from an energy channel key so that
    REleASE mismatch keys (e.g. min.10.0...MeV_min.15.8...) are grouped
    under their base channel (e.g. min.10.0...MeV)."""
    return energy_key.split('_min.')[0]


def build_contingency_table_data(df, header, mode='all',
                                  parenthesized_start_datetime=None,
                                  parenthesized_end_datetime=None):
    """Build contingency table rows for one (energy_key, threshold_key) slice."""
    table_data = []
    table_color_dict = {}
    table_text_color_dict = {}
    breakdown_table_data = []
    ne_abbrev_list = list(_NE_ABBREVIATIONS.values())

    row_counter = 0
    for name, group in df.groupby('Model Category'):
        for subname, subgroup in group.groupby('Model Flavor'):
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
                if item in contingency_data and contingency_data[item] is not None:
                    if contingency_data_parenthesized is not None:
                        table_line_dict[item] = format_objects.format_parenthesized_entry(
                            contingency_data[item], contingency_data_parenthesized[item])
                    else:
                        table_line_dict[item] = str(contingency_data[item])
            table_data.append(list(table_line_dict.values()))

            color_map = {'Hits': 2, 'Misses': 3, 'False Alarms': 4, 'Correct Negatives': 5}
            for key, col_idx in color_map.items():
                table_color_dict[(row_counter, col_idx)] = config.color.associations[key]
                table_text_color_dict[(row_counter, col_idx)] = '#ffffff'

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


def build_all_clear_contingency_table(df, week_start, week_end):
    """Build All Clear Contingency Tables, one sub-table per
    (energy channel, threshold) pair.

    Returns
    -------
    text : str
        HTML for the contingency tables.
    breakdown_sections : list of (label, breakdown_table_data)
        Breakdown data per channel, for passing to
        build_evaluation_breakdown.build_evaluation_breakdown().
    """
    text = build_html.build_paragraph_title('All Clear Contingency Tables')
    text += build_html.build_regular_text(
        "Values are given in the form X (+Y), where X is the all-time quantity, "
        "and Y is the quantity added from this period's results. X is inclusive of Y.")

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

    breakdown_sections = []

    for energy_key, threshold_key in config.order.energy_channel_threshold_order:
        channel_mask = (
            (df['Energy Channel Key'].apply(_normalize_energy_key) == energy_key) &
            (df['Threshold Key'] == threshold_key)
        )
        channel_df = df[channel_mask]
        if channel_df.empty:
            continue

        label = _channel_label(energy_key, threshold_key)
        text += build_html.build_paragraph_title(label, sublevel=1)

        table_data, table_color_dict, table_text_color_dict, breakdown_table_data = \
            build_contingency_table_data(channel_df, headers, 'all', week_start, week_end)

        if table_data:
            text += build_html.build_table(
                headers, table_data,
                header_color_dict=header_color_dict,
                table_color_dict=table_color_dict,
                table_text_color_dict=table_text_color_dict)

        breakdown_sections.append((label, breakdown_table_data))

    # ADD A SINGLE FOOTNOTE IF REleASE MODELS ARE PRESENT ANYWHERE IN THE DATA.
    has_release = df['Model'].str.contains('REleASE', case=False, na=False).any()
    if has_release:
        text += build_html.build_regular_text(
            '<em>Note on HESPERIA REleASE:</em> REleASE forecasts are issued for '
            '15.8&#8209;39&nbsp;MeV protons exceeding 0.1&nbsp;pfu/MeV, but are '
            'validated here against &gt;10&nbsp;MeV protons exceeding 10&nbsp;pfu. '
            'Predicted peak fluxes from REleASE may be correlated with observed values '
            'but are not expected to match numerically, as they represent different '
            'energy channels and units.')

    text += build_html.build_divider()
    return text, breakdown_sections


def build_false_alarm_table(df):
    text = build_html.build_paragraph_title('False Alarms')
    headers = ['Model Category', 'Model Flavor', 'Forecast Issue Time',
               'Prediction Window Start', 'Prediction Window End']
    text += build_single_stat_contingency_table(df, mode='false alarm', header=headers)
    return text
