def scoreboard_call(model_list, input_time, scoreboard_type_toggle):
    """
    A function to write custom SB urls that will display the SB runs contained wthin
    the mailsphinx summary.
    
    inputs: 

    model_list: array of strings containing the names of the scoreboard models
    input_time: the end time of the event of interest - since the scoreboard works 
        best when looking from the end of the event backwards. Can be a datetime 
        object or a string (in YYYY-MM-DDTHH:MMZ format)
    scoreboard_type_toggle: a string containing either Probability or Intensity
    """
    # not currently used but keeping it around in case something changes about the
    # function call and we need to handle datetime objects 
    from datetime import datetime
    


    url = None
    date = input_time.rsplit(' ')[0]
    time = input_time.rsplit(' ')[1].rsplit('.')[0]
    # Start with building the basics of the scoreboard url
    if scoreboard_type_toggle == 'Probability':
        url_start = "https://sep.ccmc.gsfc.nasa.gov/probability/refresh=False"
        model_string = '&models='
        for models in model_list:
            if 'MAG4' in models:
                if model_string[-1] == '=':

                    model_string += 'mag4'
                else:
                    model_string += '+mag4'
            if 'MagPy' in models:
                if model_string[-1] == '=':

                    model_string += 'magpy'
                else:
                    model_string += '+magpy'
                
            if 'SWPC' in models:
                if model_string[-1] == '=':

                    model_string += 'swpc'
                else:
                    model_string += '+swpc'

            if 'SAWS-ASPECS' in models:
                if model_string[-1] == '=':

                    model_string += 'aspfore1'
                else:
                    model_string += '+aspfore1'

            if 'SAWS-ASPECS' in models:
                if model_string[-1] == '=':
                    model_string += 'aspnowtrig'
                else:
                    model_string += '+aspnowtrig'

            if 'GSU' in models:
                if model_string[-1] == '=':

                    model_string += 'gsuac'
                else:
                    model_string += '+gsuac'

            if 'SPRINTS' in models:
                if model_string[-1] == '=':

                    model_string += 'sprints'
                else:
                    model_string += '+sprints'
            # if type(input_time) == str:
            #     date = input_time.rsplit(' ')[0]
            #     time = input_time.rsplit(' ')[1].rsplit('.')[0] 
        url = url_start + model_string + "&ecs=10+100&x_min=-7&x_max=2.5&date=" + date + "&time=" + time + "&font_ts_axis=18&font_ts_hover=14&font_hm_axis=12&font_hm_hover=15"
        # if no models then return default url (otherwise it would return a link to an empty scoreboard for the chosen time period)
        if model_string == '&models=':
            url = 'https://sep.ccmc.gsfc.nasa.gov/probability/'


    elif scoreboard_type_toggle == 'Intensity':
        url_start = "https://sep.ccmc.gsfc.nasa.gov/intensity/refresh=False"
        model_string = '&models=ace+goes'
        # Putting all model subtypes here since i'm lazy
        for models in model_list:
            if 'SAWS-ASPECS' in models:
                if model_string[-1] == '=':

                    model_string += 'aspforeconst+aspforevar+aspnowconst+aspnowvar'
                else:
                    model_string += '+aspforeconst+aspforevar+aspnowconst+aspnowvar'
            if 'RELEASE' in models:
                if model_string[-1] == '=':

                    model_string += 'release60'
                else:
                    model_string += '+release60'
            if 'SEPMOD' in models:
                if model_string[-1] == '=':

                    model_string += 'sepmodall'
                else:
                    model_string += '+sepmodall'
            if 'SEPSTER' in models:
                if model_string[-1] == '=':

                    model_string += 'sepsterall'
                else:
                    model_string += '+sepsterall'
            if 'SEPSTER2D' in models:
                if model_string[-1] == '=':

                    model_string += 'sepster2dall'
                else:
                    model_string += '+sepster2dall'
            if 'UMASEP' in models:
                if model_string[-1] == '=':

                    model_string += 'umasep'
                else:
                    model_string += '+umasep'
            if 'iPATH_CME' in models:
                if model_string[-1] == '=':
                    model_string += 'ipathcme'
        url = url_start + model_string + "&ecs=all&x_min=-7&x_max=2.5&y_min=-2&y_max=6&date=" + date + "&time=" + time + "&font_ts_axis=18&font_ts_hover=14&font_hm_axis=12&font_hm_hover=15&font_hm_annot=15&afow=6"
        # if no models then return default url (otherwise it would return a link to an empty scoreboard for the chosen time period)
        if model_string == '&models=ace+goes':
            url = 'https://sep.ccmc.gsfc.nasa.gov/intensity/'
    # print(url)

   







    return url
