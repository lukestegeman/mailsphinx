from ..utils import config

import datetime
import numpy as np
import pandas as pd
import re

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
    if isinstance(value, str): # HACKY FIX
        if ':00+00:00' in value:
            return value.rstrip(':00+00:00')
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

def convert_cids_to_image_paths(text):
    pattern = r'src="cid:([^"]*")'
    matches = re.findall(pattern, text)
    swapped_dict = {value : key for key, value in config.image.cid_dict.items()}
    for match in matches:
        text = text.replace('cid:' + match, swapped_dict[match[:-1]] + '"')
    return text
     
    





