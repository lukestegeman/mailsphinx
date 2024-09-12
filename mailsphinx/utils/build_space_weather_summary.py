from ..utils import build_html
from ..utils import build_legend
from ..utils import config
from ..utils import manipulate_dates

import io
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import requests
import warnings

plt.rcParams['font.family'] = config.plot.font
plt.rcParams['font.size'] = config.plot.fontsize 

def build_space_weather_summary(historical=False, start_datetime=None, end_datetime=None, convert_image_to_base64=False):
    goes_proton_df = download_flux(flux_type='proton', start_datetime=start_datetime, end_datetime=end_datetime)
    goes_xray_df = download_flux(flux_type='xray', start_datetime=start_datetime, end_datetime=end_datetime)
    ace_electron_df = download_flux(flux_type='electron', start_datetime=start_datetime, end_datetime=end_datetime)
    plot_flux(goes_xray_df, goes_proton_df, ace_electron_df)
    text = build_html.build_section_title('Space Weather Summary')
    # MAKE LEGEND
    build_legend.build_legend()
    text += build_html.build_image(os.path.join(config.path.email_image, 'legend.jpg'), write_as_base64=convert_image_to_base64)
    #text += build_html.build_image(os.path.join(config.path.static_image, 'legend.jpg'), write_as_base64=convert_image_to_base64)
    text += build_html.build_image(os.path.join(config.path.email_image, 'goes-flux.jpg'), write_as_base64=convert_image_to_base64)
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

def download_flux(flux_type, historical=False, start_datetime=None, end_datetime=None):
    if flux_type == 'proton' or flux_type == 'xray':
        df = download_goes_flux(flux_type, start_datetime=start_datetime, end_datetime=end_datetime)
    elif flux_type == 'electron':
        df = download_ace_epam_flux(start_datetime, end_datetime)
    return df

def download_ace_epam_flux(start_datetime, end_datetime):
    if end_datetime < config.time.iswa_minimum_time:
        print('WARNING: ISWA does not carry data prior to 2010-04-14T00:00:00Z. Expect empty plots.')
    base_url = 'https://iswa.gsfc.nasa.gov/IswaSystemWebApp/hapi/data?'
    flux_type_url = 'id=ace_epam_P5M'
    url = base_url + flux_type_url + '&time.min=' + start_datetime.strftime('%Y-%m-%dT%H:%M:%S.%fZ') + '&time.max=' + end_datetime.strftime('%Y-%m-%dT%H:%M:%S.%fZ') + '&format=csv'
    response = rerequest(url) 
    if response.status_code == 200:
        data = response.text
        df = pd.read_csv(io.StringIO(data))
        df.columns = ['time_tag', '38-53 keV', '175-315 keV', '47-68 keV (protons)', '115-195 keV (protons)', '310-580 keV (protons)', '795-1193 keV (protons)', '1060-1900 keV (protons)']
        df['time_tag'] = pd.to_datetime(df['time_tag'], format='%Y-%m-%dT%H:%M:%SZ', errors='coerce')
    else:
        print(f'Failed to retrieve data. HTTP Status code: {response.status_code}')
        print('Exiting...')
        exit()
    return df

def download_goes_flux(flux_type, start_datetime, end_datetime): 
    if end_datetime < config.time.iswa_minimum_time:
        print('WARNING: ISWA does not carry data prior to 2010-04-14T00:00:00Z. Expect empty plots.')
    base_url = 'https://iswa.gsfc.nasa.gov/IswaSystemWebApp/hapi/data?'
    if flux_type == 'proton':
        flux_type_url = 'id=goesp_part_flux_P5M'
    elif flux_type == 'xray':
        flux_type_url = 'id=goesp_xray_flux_P1M'
    url = base_url + flux_type_url + '&time.min=' + start_datetime.strftime('%Y-%m-%dT%H:%M:%S.%fZ') + '&time.max=' + end_datetime.strftime('%Y-%m-%dT%H:%M:%S.%fZ') + '&format=csv'
    response = rerequest(url) 
    if response.status_code == 200:
        data = response.text
        df = pd.read_csv(io.StringIO(data))
        if flux_type == 'proton':
            df.columns = ['time_tag', '>=1 MeV', '>=5 MeV', '>=10 MeV', '>=30 MeV', '>=50 MeV', '>=100 MeV', 'E>=0.8 MeV', 'E>=2 MeV', 'E>=4 MeV', '>=60 MeV', '>=500 MeV']
        elif flux_type == 'xray':
            df.columns = ['time_tag', 'short', 'long']
        df['time_tag'] = pd.to_datetime(df['time_tag'], format='%Y-%m-%dT%H:%M:%SZ', errors='coerce')
    else:
        print(f'Failed to retrieve data. HTTP Status code: {response.status_code}')
        print('Exiting...')
        exit()
    return df

def plot_flux(df_xray, df_proton, df_electron): 

    fig, (ax_xray, ax_electron, ax_proton) = plt.subplots(3, 1, sharex=True, figsize=(config.image.width, config.image.height * 2.5), gridspec_kw={'height_ratios' : [2, 1, 2], 'hspace' : 0.1} )
    t_low_xray = np.min(df_xray['time_tag'])
    t_high_xray = np.max(df_xray['time_tag'])
    t_low_proton = np.min(df_proton['time_tag'])
    t_high_proton = np.max(df_proton['time_tag'])
    t_low_electron = np.min(df_electron['time_tag'])
    t_high_electron = np.max(df_electron['time_tag'])
    t_low = manipulate_dates.round_to_nearest_day(min(min(t_low_xray, t_low_proton), t_low_electron))
    t_high = manipulate_dates.round_to_nearest_day(max(max(t_high_xray, t_high_proton), t_high_electron))

    df_xray['time_tag_long'] = df_xray['time_tag_short'] = df_xray['time_tag']
    df_proton['time_tag_1'] = df_proton['time_tag_5'] = df_proton['time_tag_10'] = df_proton['time_tag_30'] = df_proton['time_tag_50'] = df_proton['time_tag_60'] = df_proton['time_tag_100'] = df_proton['time_tag_500'] = df_proton['time_tag']
    df_electron['time_tag_1'] = df_electron['time_tag_2'] = df_electron['time_tag']

    ax_xray.plot(df_xray['time_tag_long'], df_xray['long'], label='Long', color=config.color.associations['Long X-Ray Flux'])
    ax_xray.plot(df_xray['time_tag_short'], df_xray['short'], label='Short', color=config.color.associations['Short X-Ray Flux'])
    ax_xray.grid(axis='both')
    ax_xray.set_yscale('log')
    ax_xray.set_ylim([1e-9, max(1e-2, np.max(df_xray['long']))])
    ax_xray.set_ylabel('GOES X-Ray Flux\n[W m$^\mathregular{-2}$]')
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


    # ACCOUNT FOR MISSING DATA
    df_electron['time_difference'] = df_electron['time_tag'].diff().dt.total_seconds()
    segments = []
    current_segment = [df_electron.iloc[0]]
    for i in range(1, len(df_electron)):
        if df_electron['time_difference'].iloc[i] > 5 * 60 + 1:
            segments.append(pd.DataFrame(current_segment))
            current_segment = []
        current_segment.append(df_electron.iloc[i])

    for segment in segments:
        ax_electron.plot(segment['time_tag_1'], segment['38-53 keV'], color=config.color.associations['38-53 keV Electron Flux'])
        ax_electron.plot(segment['time_tag_2'], segment['175-315 keV'], color=config.color.associations['175-315 keV Electron Flux'])
    ax_electron.grid(axis='both')
    ax_electron.set_yscale('log')
    ax_electron.set_ylim([1e+1, max(1e+4, df_electron['38-53 keV'].max() * 2)])
    ax_electron.set_ylabel('ACE Differential Electron Flux\n[electron cm$^\mathregular{-2}$ sr$^\mathregular{-1}$ s$^\mathregular{-1}$ MeV$^\mathregular{-1}$]')


    #ax_proton.plot(df_proton['time_tag_1'], df_proton['>=1 MeV'], color=config.color.associations['>=1 MeV Proton Flux'])
    ax_proton.plot(df_proton['time_tag_5'], df_proton['>=5 MeV'], color=config.color.associations['>=5 MeV Proton Flux'])
    ax_proton.plot(df_proton['time_tag_10'], df_proton['>=10 MeV'], color=config.color.associations['>=10 MeV Proton Flux'])
    ax_proton.plot(df_proton['time_tag_30'], df_proton['>=30 MeV'], color=config.color.associations['>=30 MeV Proton Flux'])
    ax_proton.plot(df_proton['time_tag_50'], df_proton['>=50 MeV'], color=config.color.associations['>=50 MeV Proton Flux'])
    ax_proton.plot(df_proton['time_tag_60'], df_proton['>=60 MeV'], color=config.color.associations['>=60 MeV Proton Flux'])
    ax_proton.plot(df_proton['time_tag_100'], df_proton['>=100 MeV'], color=config.color.associations['>=100 MeV Proton Flux']) 
    ax_proton.plot(df_proton['time_tag_500'], df_proton['>=500 MeV'], color=config.color.associations['>=500 MeV Proton Flux'])
    ax_proton.plot([t_low, t_high], [10, 10], color=config.color.associations['>=10 MeV Proton Flux'], linestyle=':', linewidth=1)
    ax_proton.plot([t_low, t_high], [1, 1], color=config.color.associations['>=100 MeV Proton Flux'], linestyle=':', linewidth=1)
    ax_proton.grid(axis='both')
    ax_proton.set_yscale('log')
    ax_proton.set_ylim([10 ** (-1), max(1e+2, np.max(df_proton['>=5 MeV']))])
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', category=UserWarning)
        ax_proton.set_xticklabels(ax_proton.get_xticklabels(), rotation=45)
    ax_proton.set_ylabel('GOES Integral Proton Flux\n[proton cm$^\mathregular{-2}$ sr$^\mathregular{-1}$ s$^\mathregular{-1}$]')

    with warnings.catch_warnings():
        warnings.simplefilter('ignore', category=UserWarning)
        plt.tight_layout()
    #fig.patch.set_facecolor('green')
    plt.subplots_adjust(left=config.html.left_padding_fraction) 
    plt.savefig(os.path.join(config.path.email_image, 'goes-flux.jpg'), dpi=config.image.dpi, bbox_inches=0) 
    plt.close()

