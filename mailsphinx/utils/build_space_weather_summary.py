from ..utils import manipulate_dates
from ..utils import build_html
#from ..utils import build_legend
from ..utils import config

import requests
import pandas as pd
import numpy as np
import io
import matplotlib.pyplot as plt
import os
import matplotlib
plt.rcParams['font.family'] = config.plot.font
plt.rcParams['font.size'] = config.plot.fontsize 

def build_space_weather_summary(historical=False, start_datetime=None, end_datetime=None):
    goes_proton_df = download_goes_flux(flux_type='proton', historical=historical, start_datetime=start_datetime, end_datetime=end_datetime)
    goes_xray_df = download_goes_flux(flux_type='xray', historical=historical, start_datetime=start_datetime, end_datetime=end_datetime)
    plot_goes_flux(goes_xray_df, goes_proton_df, historical=historical)
    text = build_html.build_section_title('Space Weather Summary')
    # MAKE LEGEND
    #build_legend.build_legend()
    #text += build_html.build_image(os.path.join(config.path.email_image, 'legend.jpg'))
    text += build_html.build_image(os.path.join(config.path.static_image, 'legend.jpg'))
    text += build_html.build_image(os.path.join(config.path.email_image, 'goes-flux.jpg'))
    text += build_html.build_divider()
    return text

def rerequest(url, tries=0):
    """
    Runs requests.get() until a response is received to avoid chokepoints

    Parameters
    ----------
    url : string
        URL where desired data resides
    tries [untouched by user] : int
        Number of attempts
    """

    # end the requesting process if tries > 5
    if tries > 5:
        raise Exception(url + " refuses to respond after 5 attempts. Exiting.")

    try:
        output = requests.get(url, timeout=10.0)
        return output
    except requests.exceptions.Timeout as e:
        return rerequest(url, tries + 1)

def download_goes_flux(flux_type, historical=False, start_datetime=None, end_datetime=None): 
    if historical:
        assert(start_datetime is not None), 'start_datetime cannot be None in historical mode.'
        assert(end_datetime is not None), 'end_datetime cannot be None in historical mode.'
        if end_datetime < config.time.iswa_minimum_time:
            print('WARNING: ISWA does not carry data prior to 2010-04-14T00:00:00Z. Expect empty plots.')
        base_url = 'https://iswa.gsfc.nasa.gov/IswaSystemWebApp/hapi/data?'
        if flux_type == 'proton':
            flux_type_url = 'id=goesp_part_flux_P5M'
        elif flux_type == 'xray':
            flux_type_url = 'id=goesp_xray_flux_P1M'
        url = base_url + flux_type_url + '&time.min=' + start_datetime.strftime('%Y-%m-%dT%H:%M:%S.%fZ') + '&time.max=' + end_datetime.strftime('%Y-%m-%dT%H:%M:%S.%fZ') + '&format=csv'
    else:
        # REAL TIME
        if flux_type == 'proton':
            url = 'https://services.swpc.noaa.gov/json/goes/primary/integral-protons-7-day.json' 
            #url = 'https://services.swpc.noaa.gov/json/goes/secondary/integral-protons-7-day.json'
        elif flux_type == 'xray':    
            url = 'https://services.swpc.noaa.gov/json/goes/primary/xrays-7-day.json'
            #url = 'https://services.swpc.noaa.gov/json/goes/secondary/xrays-7-day.json'
    response = rerequest(url) 
    if response.status_code == 200:
        if historical:
            data = response.text
            df = pd.read_csv(io.StringIO(data))
            if flux_type == 'proton':
                df.columns = ['time_tag', '>=1 MeV', '>=5 MeV', '>=10 MeV', '>=30 MeV', '>=50 MeV', '>=100 MeV', 'E>=0.8 MeV', 'E>=2 MeV', 'E>=4 MeV', '>=60 MeV', '>=500 MeV']
            elif flux_type == 'xray':
                df.columns = ['time_tag', 'short', 'long']
            df['time_tag'] = pd.to_datetime(df['time_tag'])
        else:
            data = response.json()
            df = pd.DataFrame(data)
            df['time_tag'] = pd.to_datetime(df['time_tag'])
    else:
        print(f'Failed to retrieve data. HTTP Status code: {response.status_code}')
        print('Exiting...')
        exit()
    return df

def plot_goes_flux(df_xray, df_proton, historical=False): 

    fig, (ax_xray, ax_proton) = plt.subplots(2, 1, sharex=True, figsize=(config.image.width, config.image.height * 2), gridspec_kw={'height_ratios' : [1, 1], 'hspace' : 0.1} )
    t_low_xray = np.min(df_xray['time_tag'])
    t_high_xray = np.max(df_xray['time_tag'])
    t_low_proton = np.min(df_proton['time_tag'])
    t_high_proton = np.max(df_proton['time_tag'])
    t_low = manipulate_dates.round_to_nearest_day(min(t_low_xray, t_low_proton))
    t_high = manipulate_dates.round_to_nearest_day(max(t_high_xray, t_high_proton))

    if historical:
        df_xray['time_tag_long'] = df_xray['time_tag_short'] = df_xray['time_tag']
        df_proton['time_tag_1'] = df_proton['time_tag_5'] = df_proton['time_tag_10'] = df_proton['time_tag_30'] = df_proton['time_tag_50'] = df_proton['time_tag_60'] = df_proton['time_tag_100'] = df_proton['time_tag_500'] = df_proton['time_tag']
    else:
        long_condition = df_xray['energy'] == '0.1-0.8nm'
        short_condition = df_xray['energy'] == '0.05-0.4nm'
        df_xray['time_tag_long'] = df_xray[long_condition]['time_tag']
        df_xray['time_tag_short'] = df_xray[short_condition]['time_tag']
        df_xray['long'] = df_xray[long_condition]['flux']
        df_xray['short'] = df_xray[short_condition]['flux']
        p1_condition = df_proton['energy'] == '>=1 MeV' 
        p5_condition = df_proton['energy'] == '>=5 MeV'
        p10_condition = df_proton['energy'] == '>=10 MeV'
        p30_condition = df_proton['energy'] == '>=30 MeV'
        p50_condition = df_proton['energy'] == '>=50 MeV'
        p60_condition = df_proton['energy'] == '>=60 MeV'
        p100_condition = df_proton['energy'] == '>=100 MeV'
        p500_condition = df_proton['energy'] == '>=500 MeV'
        df_proton['time_tag_1'] = df_proton[p1_condition] 
        df_proton['time_tag_5'] = df_proton[p5_condition]
        df_proton['time_tag_10'] = df_proton[p10_condition]
        df_proton['time_tag_30'] = df_proton[p30_condition]
        df_proton['time_tag_50'] = df_proton[p50_condition]
        df_proton['time_tag_60'] = df_proton[p60_condition]
        df_proton['time_tag_100'] = df_proton[p100_condition] 
        df_proton['time_tag_500'] = df_proton[p100_condition] 
        df_proton['>=1 MeV'] = df_proton[p1_condition]['flux']
        df_proton['>=5 MeV'] = df_proton[p5_condition]['flux']
        df_proton['>=10 MeV'] = df_proton[p10_condition]['flux']
        df_proton['>=30 MeV'] = df_proton[p30_condition]['flux']
        df_proton['>=50 MeV'] = df_proton[p50_condition]['flux']
        df_proton['>=60 MeV'] = df_proton[p60_condition]['flux']
        df_proton['>=100 MeV'] = df_proton[p100_condition]['flux'] 
        df_proton['>=500 MeV'] = df_proton[p100_condition]['flux']

    ax_xray.plot(df_xray['time_tag_long'], df_xray['long'], label='Long', color=config.color.associations['Long X-Ray Flux'])
    ax_xray.plot(df_xray['time_tag_short'], df_xray['short'], label='Short', color=config.color.associations['Short X-Ray Flux'])
    #ax_xray.legend(loc='upper left', bbox_to_anchor=(1.05, 1.0))
    ax_xray.grid(axis='both')
    ax_xray.set_yscale('log')
    ax_xray.set_ylim([1e-9, max(1e-2, np.max(df_xray['long']))])
    ax_xray.set_ylabel('GOES X-Ray Flux [Watt m$^\mathregular{-2}$]')
    ax_xray.set_xlim([t_low, t_high])
    ax_xray_class = ax_xray.twinx()
    labels = ['A', 'B', 'C', 'M', 'X']
    positions = [10 ** (-7.5), 10 ** (-6.5), 10 ** (-5.5), 10 ** (-4.5), 10 ** (-3.5)]
    ax_xray_class.set_yticks([])
    ax_xray_class.set_ylim(ax_xray.get_ylim())
    ax_xray_class.set_yscale('log')
    ax_xray_class.set_yticks(positions)
    ax_xray_class.set_yticklabels(labels)
    ax_xray_class.yaxis.set_label_position('right')
    ax_proton.plot(df_proton['time_tag_1'], df_proton['>=1 MeV'], label='$\geq$ 1 MeV', color=config.color.associations['>=1 MeV Proton Flux'])
    ax_proton.plot(df_proton['time_tag_5'], df_proton['>=5 MeV'], label='$\geq$ 5 MeV', color=config.color.associations['>=5 MeV Proton Flux'])
    ax_proton.plot(df_proton['time_tag_10'], df_proton['>=10 MeV'], label='$\geq$ 10 MeV', color=config.color.associations['>=10 MeV Proton Flux'])
    ax_proton.plot(df_proton['time_tag_30'], df_proton['>=30 MeV'], label='$\geq$ 30 MeV', color=config.color.associations['>=30 MeV Proton Flux'])
    ax_proton.plot(df_proton['time_tag_50'], df_proton['>=50 MeV'], label='$\geq$ 50 MeV', color=config.color.associations['>=50 MeV Proton Flux'])
    ax_proton.plot(df_proton['time_tag_60'], df_proton['>=60 MeV'], label='$\geq$ 60 MeV', color=config.color.associations['>=60 MeV Proton Flux'])
    ax_proton.plot(df_proton['time_tag_100'], df_proton['>=100 MeV'], label='$\geq$ 100 MeV', color=config.color.associations['>=100 MeV Proton Flux']) 
    ax_proton.plot(df_proton['time_tag_500'], df_proton['>=500 MeV'], label='$\geq$ 500 MeV', color=config.color.associations['>=500 MeV Proton Flux'])
    ax_proton.plot([t_low, t_high], [10, 10], color=config.color.associations['>=10 MeV Proton Flux'], linestyle=':', linewidth=1)
    ax_proton.plot([t_low, t_high], [1, 1], color=config.color.associations['>=100 MeV Proton Flux'], linestyle=':', linewidth=1)
    #ax_proton.legend(loc='upper left', bbox_to_anchor=(1.05, 1.0))
    ax_proton.grid(axis='both')
    ax_proton.set_yscale('log')
    ax_proton.set_ylim([10 ** (-1), max(1e+2, np.max(df_proton['>=1 MeV']))])
    ax_proton.set_xlabel('UTC')
    ax_proton.set_xticklabels(ax_proton.get_xticklabels(), rotation=45)
    ax_proton.set_ylabel('GOES Integral Proton Flux [proton cm$^\mathregular{-2}$ sr$^\mathregular{-1}$ s$^\mathregular{-1}$]')

    plt.tight_layout()
    plt.subplots_adjust(left=config.html.left_padding_fraction) 
    plt.savefig(os.path.join(config.path.email_image, 'goes-flux.jpg'), dpi=config.image.dpi // 2, bbox_inches=0) 


