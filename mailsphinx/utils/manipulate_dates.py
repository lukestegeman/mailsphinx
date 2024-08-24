from ..utils import config

import datetime
import pandas as pd
import pytz

def round_to_nearest_day(dt):
    half_day = datetime.timedelta(days=0.5)
    start_of_day = dt.replace(hour=0, minute=0, second=0, microsecond=0)
    delta = dt - start_of_day
    if delta >= half_day:
        add = datetime.timedelta(days=1)
    else:
        add = datetime.timedelta(days=0)
    rounded_datetime = start_of_day + add
    return rounded_datetime

# MAILSPHINX DATE BOUNDARIES
def get_most_recent_weekday(right_now, weekday):
    """
    Computes the most recent {weekday}'s date.
    """
    days_to_weekday = (right_now.weekday() - config.time.weekday_index[weekday]) % 7
    weekday_date = right_now - datetime.timedelta(days=days_to_weekday)
    return weekday_date

def get_weekday_before(right_now, weekday):
    most_recent_weekday = get_most_recent_weekday(right_now, weekday)
    weekday_date = most_recent_weekday - datetime.timedelta(days=7)
    return weekday_date

def get_mailsphinx_boundaries(start_weekday, end_weekday):
    """
    Computes the time period for which the MailSPHINX weekly report email applies.
    start_weekday starts at 00:00:00 GMT on selected day of week, end_weekday ends at 00:00:00 GMT on selected day of week

    Parameters
    ----------
    start_weekday : string (Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday)

    end_weekday : string (Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday)

    Returns
    -------
    start_datetime : datetime object

    end_datetime : datetime object
    """
    start_weekday = start_weekday.capitalize()
    end_weekday = end_weekday.capitalize()

    assert(start_weekday in list(config.time.weekday_index.keys())), 'start_weekday must be a day of the week' 
    assert(end_weekday in list(config.time.weekday_index.keys())), 'end_weekday must be a day of the week'

    gmt = pytz.timezone('GMT')
    now_gmt = datetime.datetime.now(gmt).replace(hour=0, minute=0, second=0, microsecond=0)
    now_weekday = now_gmt.weekday()

    # WHEN WAS THE MOST RECENT end_weekday?
    end_datetime = pd.to_datetime(get_most_recent_weekday(now_gmt, end_weekday))

    # WHEN WAS THE start_weekday before that?
    start_datetime = pd.to_datetime(get_weekday_before(now_gmt, start_weekday))

    return start_datetime, end_datetime


def identify_datetime_columns(df):
    datetime_columns = []
    for col in df.columns:
        if df[col].dtype == object:
            try:
                # Convert to datetime and check for any non-NaT values
                if pd.to_datetime(df[col], errors='coerce').notna().any():
                    datetime_columns.append(col)
            except Exception as e:
                continue
    return datetime_columns

def convert_to_datetime(df, datetime_cols):
    for col in datetime_cols:
        df[col] = pd.to_datetime(df[col], errors='coerce')
        df[col] = df[col].dt.tz_localize('UTC')
    return df

