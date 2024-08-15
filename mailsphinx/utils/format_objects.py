import pandas as pd
import numpy as np
import re
import datetime


# FORMATTING
def format_data(value):
    if type(value) == type(datetime.datetime):
        return str(value)
    elif type(value) == type(pd.Timestamp(year=2000, month=1, day=1)):
        return str(value)
    elif type(value) == str:
        return value
    elif np.isnan(value):
        return 'N/A'
    else:
        if (value >= 10000) or (value <= 0.0001):
            return '{:.4E}'.format(value)
        else:
            return '{:.4f}'.format(value)

def format_df_datetime(value):
    if isinstance(value, (datetime.datetime, pd.Timestamp)):
        if pd.isna(value):
            return value
        return value.strftime('%Y-%m-%d %H:%M')
    return value

def to_snake_case(string):
    string = re.sub('([a-z])([A-Z])', r'\1_\2', string)
    string = re.sub(r'[\s-]+', '_', string)
    string = re.sub(r'_+', '_', string)
    string = string.lower()
    string = string.strip('_')
    return string

def to_hyphen_case(string):
    return to_snake_case(string).replace('_', '-')

def is_whole(value):
    if isinstance(value, (int, float)):
        return (value % 1 == 0.0)
    return False

def string_as_whole(value):
    if is_whole(value):
        return str(int(value))
    return '{:.1f}'.format(value)

def format_energy_threshold(value):
    return '&ge; ' + string_as_whole(value)

def format_flux_threshold(value):
    return '&ge; ' + string_as_whole(value)

def format_parenthesized_entry(a, b):
    entry = str(a) + ' (+' + str(b) + ')'
    return entry
