from ..utils import manipulate_keys
from ..utils import build_html

# BUILD OVERVIEW SECTION
def build_overview_table_row(df, start_datetime):
    """
    Builds a table row for the Overview section of the email body.
    
    Parameters
    ----------
    df : pandas dataframe
    
    start_datetime : pandas Timestamp    

    Returns
    -------
    row : list of string
    """
    row = []
    row.append('Since ' + start_datetime.strftime('%Y-%m-%d %H:%M'))
   
    # NUMBER OF FORECASTS 
    number_forecasts = len(df)
    row.append(str(number_forecasts))
    
    # NUMBER OF NOT CLEAR FORECASTS
    number_forecasts_not_clear = len(df['Predicted SEP All Clear'] == False)
    row.append(str(number_forecasts_not_clear))

    # NUMBER OF FORECASTS THAT PREDICTED PEAK FLUXES ABOVE THRESHOLD
    # INCLUDES FORECASTS THAT ONLY PREDICT MAX FLUX, ONLY PREDICT ONSET PEAK FLUX, OR BOTH
    if number_forecasts == 0:
        number_forecasts_above_threshold_peak_flux = 0
    else:
        thresholds = manipulate_keys.convert_threshold_key_to_float(df['Threshold Key'])
        above_threshold_peak_flux_condition = (df['Predicted SEP Peak Intensity Max (Max Flux)'] >= thresholds) + (df['Predicted SEP Peak Intensity (Onset Peak)'] >= thresholds) > 0
        number_forecasts_above_threshold_peak_flux = len(df[above_threshold_peak_flux_condition] == True)
    row.append(str(number_forecasts_above_threshold_peak_flux))
 
    # NUMBER OF THRESHOLD CROSSINGS (>10 MeV, >10 pfu)
    threshold_crossings_10_10_condition = (df['Observed SEP All Clear'] == False) * (df['Energy Channel Key'] == 'min.10.0.max.-1.0.units.MeV') * (df['Threshold Key'] == 'threshold.10.0.units.1 / (cm2 s sr)')
    number_threshold_crossings_10_10 = len(df[threshold_crossings_10_10_condition] == True)
    row.append(str(number_threshold_crossings_10_10))
    
    # NUMBER OF THRESHOLD CROSSINGS (>100 MeV, >1 pfu)
    threshold_crossings_100_1_condition = (df['Observed SEP All Clear'] == False) * (df['Energy Channel Key'] == 'min.100.0.max.-1.0.units.MeV') * (df['Threshold Key'] == 'threshold.1.0.units.1 / (cm2 s sr)')
    number_threshold_crossings_100_1 = len(df[threshold_crossings_100_1_condition] == True)
    row.append(str(number_threshold_crossings_100_1))

    '''
    # % OF TIME ABOVE THRESHOLD (SPE, ESPE) THIS WEEK -- FROM OBSERVATIONS
    weekly_spe_hours = np.sum(df[threshold_crossings_10_10_condition].unique()['Observed SEP Duration'])
    percent_spe_time = weekly_spe_hours / config.time.hours_per_week * 100.0
    row.append(str(percent_spe_time))    

    weekly_espe_hours = np.sum(df[threshold_crossings_100_1_condition].unique()['Observed SEP Duration'])
    percent_espe_time = weekly_espe_hours / config.time.hours_per_week * 100.0
    row.append(str(percent_espe_time))

    number_alltime_events_spe = 
    #number_alltime_events_espe = ?
    '''    

    return row    

def build_overview_section(sphinx_df, week_start, week_end, year_start, first_forecast_datetime, weekly_forecasts, yearly_forecasts):
    """
    Writes the html that makes up the Overview section of the email body.

    Parameters
    ----------
    sphinx_df : SPHINX dataframe

    week_start : datetime

    week_end : datetime
    
    year_start : datetime
    
    weekly_forecasts : dataframe
    
    yearly_forecasts : dataframe
    
    Returns
    -------
    text : string
    """
    # WRITE HTML TABLE FROM LIST OF LISTS
    table_data = []
    dataframe_segments = [weekly_forecasts, yearly_forecasts, sphinx_df]
    start_segments = [week_start, year_start, first_forecast_datetime]
    for df, start in zip(dataframe_segments, start_segments):
        table_data.append(build_overview_table_row(df, start))
        
    headers = ['Time Period', 'Forecasts', 'Not Clear Forecasts', 'Above Threshold Peak Flux Forecasts', 'Threshold Crossings (>10 MeV, >10 pfu)', 'Threshold Crossings (>100 MeV, >1 pfu)']
    
    text = build_html.build_section_title('Overview')
    text += build_html.build_table(headers, table_data)
    text += build_html.build_divider()


    #text += 'Number of forecasts this week: ' + str(number_weekly_forecasts) + '<br><br>'
    #text += 'Number of not clear forecasts this week: ' + str(number_weekly_forecasts_not_clear) + '<br><br>'
    #text += 'Number of above threshold peak flux forecasts this week: ' + str(number_weekly_forecasts_peak_flux_above_threshold) + '<br><br>'

    '''
    # % OF TIME ABOVE THRESHOLD (SPE, ESPE) THIS WEEK -- FROM OBSERVATIONS
    fraction_weekly_spe_time = 
    fraction_weekly_espe_time = 

    # NUMBER OF COMPLETE EVENTS THIS WEEK -- FROM OBSERVATIONS
    number_weekly_complete_events_spe = 
    number_weekly_complete_events_espe = 

    # NUMBER OF FORECASTS, ALL TIME -- FROM SPHINX
    number_alltime_forecasts = len(sphinx_df)

    # NUMBER OF EVENTS, ALL TIME -- FROM OBSERVATIONS?
    #number_alltime_events_spe = ?
    #number_alltime_events_espe = ?
    '''    


    return text
