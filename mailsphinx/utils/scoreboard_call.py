import datetime
import pandas as pd

def scoreboard_call(model_list, input_time, scoreboard_type_toggle):
    """
    A function to write custom CCMC SEP Scoreboard urls that will display the Scoreboard runs contained wthin
    the MailSPHINX summary.
    
    Parameters
    ----------
    model_list : array of string 
                 contains the names of the scoreboard models
    
    input_time: datetime object OR string (YYYY-MM-DDTHH:MMZ format)
                end time of the event of interest - since the scoreboard works 
                best when looking from the end of the event backwards. 

    scoreboard_type_toggle : string (options: 'Probability', 'Intensity')

    Returns
    -------
    url : string

    """
    url = None
   
    if isinstance(input_time, datetime.datetime) or isinstance(input_time, pd.Timestamp):
        date = input_time.date().strftime('%Y-%m-%d')
        time = input_time.time().strftime('%H:%M')
    elif type(input_time) == str:
        date = input_time.rsplit(' ')[0]
        time = input_time.rsplit(' ')[1].rsplit('.')[0]
    
    probability_models = {'MAG4' : 'mag4',
                          'MagPy' : 'magpy',
                          'SAWS-ASPECS' : 'aspfore1+aspnowtrig',
                          'GSU' : 'gsuac',
                          'SPRINTS' : 'sprints'}

    intensity_models = {'SAWS-ASPECS' : 'aspforeconst+aspforevar+aspnowconst+aspnowvar',
                        'RELEASE' : 'release60',
                        'SEPMOD' : 'sepmodall',
                        'SEPSTER' : 'sepsterall',
                        'SEPSTEP2D' : 'sepster2dall',
                        'UMASEP' : 'umasep',
                        'IPATH_CME' : 'ipathcme'}

    if scoreboard_type_toggle == 'Probability':
        exclude = []
        url_start = 'https://sep.ccmc.gsfc.nasa.gov/probability/refresh=False'
        model_string = '&models='
        for key, value in probability_models.items():
            for model in model_list:
                if key in model and not (key in exclude):
                    if model_string[-1] != '=':
                        model_string += '+'
                    model_string += value
                    exclude.append(key)
        if model_string == '&models=':
            url = url_start + ''
        else:
            url = url_start + model_string + "&ecs=10+100&x_min=-7&x_max=2.5&date=" + date + "&time=" + time + "&font_ts_axis=18&font_ts_hover=14&font_hm_axis=12&font_hm_hover=15"
    
    elif scoreboard_type_toggle == 'Intensity':
        exclude = []
        url_start = 'https://sep.ccmc.gsfc.nasa.gov/intensity/refresh=False'
        model_string = '&models=ace+goes'
        for key, value in intensity_models.items():
            for model in model_list:
                if key in model and not (key in exclude):
                    model_string += '+'
                    model_string += value
                    exclude.append(key)
        if model_string == '&models=ace+goes':
            url = url_start + ''
        else:
            url = url_start + model_string + "&ecs=all&x_min=-7&x_max=2.5&y_min=-2&y_max=6&date=" + date + "&time=" + time + "&font_ts_axis=18&font_ts_hover=14&font_hm_axis=12&font_hm_hover=15&font_hm_annot=15&afow=6"

    return url

