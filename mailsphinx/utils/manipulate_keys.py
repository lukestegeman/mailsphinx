import numpy as np
import pandas as pd

# MANIPULATION OF ENERGY CHANNEL KEYS AND THRESHOLD KEYS
def convert_energy_threshold_floats_to_string(energy_threshold_low, energy_threshold_high):
    """
    Converts the energy threshold keys to a string (e.g., > 10 MeV).

    Parameters
    ----------
    energy_threshold_low : float

    energy_threshold_high : float

    Returns
    -------
    energy_threshold_string : string
    """
    
    if energy_threshold_high == np.inf:
        energy_threshold_string = '> ' + str(int(energy_threshold_low)) + ' MeV'
    else:
        energy_threshold_string = str(int(energy_threshold_low)) + ' < E < ' + str(int(energy_threshold_high)) + ' MeV'
    return energy_threshold_string

def convert_energy_key_to_floats(energy_key):
    """
    Converts the energy channel key to two floats (lower, upper).
    
    Parameters
    ----------
    energy_key : string    

    Returns
    -------
    energy_threshold_low : float [MeV]
    
    energy_threshold_high : float [MeV]
    """
    unit_dict = {'MeV' : 1}
    split_energy_key = energy_key.split('.units.')
    split_energy = split_energy_key[0].split('.max.')
    nominal_value_low = float(split_energy[0].lstrip('min.'))
    nominal_value_high = float(split_energy[1])
    if '_' in split_energy_key[1]:
        unit, mismatch_key = split_energy_key[1].split('_')
    else:
        unit = split_energy_key[1]
        mismatch_key = None
    unit_multiplier = unit_dict[unit]
    energy_threshold_low = nominal_value_low * unit_multiplier
    energy_threshold_high = nominal_value_high * unit_multiplier
    if energy_threshold_high < 0:
        energy_threshold_high = np.inf
    return energy_threshold_low, energy_threshold_high, mismatch_key

def convert_energy_key_to_string(energy_key):
    energy_threshold_low, energy_threshold_high, mismatch_key = convert_energy_key_to_floats(energy_key)
    energy_threshold_string = convert_energy_threshold_floats_to_string(energy_threshold_low, energy_threshold_high)
    return energy_threshold_string

def convert_threshold_float_to_string(threshold):
    """
    Converts the flux threshold to a string (e.g., > 10 pfu)
    
    Parameters
    ----------
    threshold : float    

    Returns
    -------
    threshold_string : string
    """
    threshold_string = '> ' + str(int(threshold)) + ' pfu'
    return threshold_string

def convert_threshold_key_to_float(threshold_key):
    """
    Converts the flux threshold key to a float.
    
    Parameters
    ----------
    threshold_key : string    

    Returns
    -------
    flux_threshold : float [cm-2 s-1 sr-1]
    """
    unit_dict = {'1 / (cm2 s sr)' : 1}
    if type(threshold_key) == pd.Series:
        split_df = threshold_key.str.split('.units.', expand=True)
        split_df.columns = ['threshold', 'unit']
        nominal_value = split_df['threshold'].str.lstrip('threshold.').astype(float)
        unit_multiplier = split_df['unit'].map(unit_dict)
    else:
        threshold, unit = threshold_key.split('.units.')
        nominal_value = float(threshold.lstrip('threshold.'))
        unit_multiplier = unit_dict[unit]
    flux_threshold = nominal_value * unit_multiplier
    return flux_threshold 

def get_min_energy_threshold(energy_key):
    return float(energy_key.split('min.')[1].split('.max')[0])

def get_min_flux_threshold(threshold_key):
    return float(threshold_key.split('threshold.')[1].split('.units')[0])


