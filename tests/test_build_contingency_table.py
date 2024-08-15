import mailsphinx.utils.build_text as bt
import mailsphinx.utils.config as cfg

import freezegun
import sys
import os

import pandas as pd
import datetime

def identify_datetime_columns(df):
    datetime_columns = []
    for col in df.columns:
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

if __name__ == '__main__':
    

    with freezegun.freeze_time('2024-07-01'):

        # FOR TESTING -- SAVES THE HTML FILE FOR CHECKING

        # GET DATAFRAME
        print('Dataframe is named "test.csv"!')
        sphinx_df = pd.read_csv(os.path.join(cfg.path.dataframe, 'test.csv'))

        datetime_columns = identify_datetime_columns(sphinx_df)
        sphinx_df = convert_to_datetime(sphinx_df, datetime_columns)


        sphinx_df = bt.categorize_column(sphinx_df, 'Model', 'Model Category', 'Model Flavor')

        # GET TIME BOUNDARIES
        week_start, week_end = bt.get_mailsphinx_boundaries(cfg.time.week_first_day, cfg.time.week_last_day)
        year_start = pd.Timestamp(datetime.datetime(day=1, month=1, year=week_start.year, hour=0, minute=0, second=0, microsecond=0), tz='UTC')
        weekly_condition = (sphinx_df['Forecast Issue Time'] < week_end) * (sphinx_df['Forecast Issue Time'] >= week_start)
        yearly_condition = (sphinx_df['Forecast Issue Time'] < week_end) * (sphinx_df['Forecast Issue Time'] >= year_start)
        first_forecast_datetime = sphinx_df['Forecast Issue Time'].min()

        # CONVERT BACK TO NAIVE DATETIME
        #sphinx_df['Forecast Issue Time'] = sphinx_df['Forecast Issue Time'].dt.tz_localize(None)

        weekly_forecasts = sphinx_df[weekly_condition]
        yearly_forecasts = sphinx_df[yearly_condition]


        weekly_forecasts.to_csv('test-weekly.csv')
        

        html = ''
        html += bt.build_head_section()    
#        html += bt.build_overview_section(sphinx_df, week_start, week_end, year_start, first_forecast_datetime, weekly_forecasts, yearly_forecasts)
#        event_forecasts, event = bt.check_for_event(sphinx_df, week_start, week_end)
#        html += bt.build_space_weather_summary()
#        if event:
#            html += bt.build_event_section(event_forecasts, week_end)





        html += bt.build_paragraph_title('All Clear Contingency Table')
        header = ['Model Category', 'Model Flavor', 'Hits', 'Misses', 'False Alarms', 'Correct Negatives', 'Forecasts', 'All-Time Report Link']
        table_data = bt.build_contingency_table_data(sphinx_df, header, 'all', week_start, week_end)
        html += bt.build_table(header, table_data)
        html += bt.build_single_stat_contingency_table(sphinx_df, 'hit', ['Model Category', 'Model Flavor', 'Forecast Issue Time', 'Prediction Window Start', 'Prediction Window End'])
        html += bt.build_single_stat_contingency_table(sphinx_df, 'miss', ['Model Category', 'Model Flavor', 'Forecast Issue Time', 'Prediction Window Start', 'Prediction Window End'])

        #html += bt.build_model_section(sphinx_df, weekly_forecasts, week_start, week_end, 'Model Performance', add_divider=False, all_clear_contingency_table=True, false_alarm_table=True, peak_flux_plot=True, probability_plot=True)
        html += bt.build_close_section()
        a = open('test-contingency-table.html', 'w')
        a.write(html)
        a.close()
