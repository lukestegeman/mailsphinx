import pandas as pd
import re

# FILTERING
def extract_common_substring(s):
    """
    Extract the common substring from a string by identifying the part
    that appears between spaces or underscores.

    Parameters
    ----------
    s : string

    Returns
    -------
    most_common : string

    leftover : string
    """
    parts = re.split(r'[ _]', s, maxsplit=1)
    most_common = s + ''
    leftover = ''
    if len(parts) > 1:
        # Return the most common substring part
        most_common = parts[0]
        leftover = parts[1]
    return most_common, leftover

def is_column_empty(df, column_name):
    """
    Determines if dataframe column is empty.
    
    Parameters
    ----------
    df : dataframe
    
    column_name : str

    Returns
    -------
    empty : bool
    """
    all_nan = df[column_name].isna().all()
    all_empty = df[column_name].apply(lambda x : x == '' or pd.isna(x)).all()
    empty = all_nan or all_empty
    return empty

def categorize_column(df, column_name, category_column_name, leftover_column_name):
    """
    Categorize strings in a DataFrame column based on a common substring.

    Parameters
    ----------
    df : dataframe

    column_name : str
    
    category_column_name : str
    
    leftover_column_name : str

    Returns
    -------
    df : dataframe
    """
    # Apply the common substring extraction to the specified column
    if df.empty:
        df[category_column_name] = None
        df[leftover_column_name] = None
        return df
    df[[category_column_name, leftover_column_name]] = df[column_name].apply(lambda x : pd.Series(extract_common_substring(x)))
    return df
