"""Display per-model validation metrics in the MailSPHINX email,
broken out by energy channel and threshold.

All metrics are read directly from sphinxval's own metrics pkl files.
MailSPHINX performs no metric computation of its own.

Each metrics section (All Clear, Probability, Max Flux × 3) renders
one sub-table per (energy channel, threshold) pair from
config.order.energy_channel_threshold_order. Models with no data for
a given channel are omitted from that channel's table.

Per-model section visibility is controlled by
mailsphinx/config/metrics_config.json.
"""

import io
import json
import os

import numpy as np
import pandas as pd

from ..utils import build_html
from ..utils import config
from ..utils import manipulate_keys


# -----------------------------------------------------------------------
# PATHS
# -----------------------------------------------------------------------

_DELTA_PKL = config.path.all_time_metrics

_METRICS_CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'config', 'metrics_config.json'
)

_SECTION_ALL_CLEAR    = 'all_clear'
_SECTION_PROBABILITY  = 'probability'
_SECTION_ONSET_PEAK   = 'max_flux_onset_peak'
_SECTION_MAX_FLUX     = 'max_flux_max_flux'
_SECTION_PRED_WINDOW  = 'max_flux_pred_window'


# -----------------------------------------------------------------------
# SPHINXVAL METRICS COLUMN MAPPINGS
# -----------------------------------------------------------------------

_AC_METRICS = [
    ('Hit Rate', 'Hit Rate'),
    ('FAR',      'False Alarm Ratio'),
    ('FAER',     'False Alarm Event Ratio'),
    ('HSS',      'Heidke Skill Score'),
    ('TSS',      'True Skill Statistic'),
]
_PROB_METRICS = [
    ('Brier Score', 'Brier Score'),
    ('AUC',         'Area Under ROC Curve'),
]
_FLUX_METRICS = [
    ('MLE',  'Median Log Error (MedLE)'),
    ('WF2',  'Percentage within a factor of 2 (%)'),
    ('WF10', 'Percentage within an Order of Magnitude (%)'),
]
_FLUX_SECTIONS = [
    (_SECTION_ONSET_PEAK,  'Onset Peak',              'peak_intensity_metrics.pkl',         'Onset Peak Flux Metrics'),
    (_SECTION_MAX_FLUX,    'Max Flux',                'peak_intensity_max_metrics.pkl',      'Max Flux Metrics'),
    (_SECTION_PRED_WINDOW, 'Max Flux in Pred Window', 'max_flux_in_pred_win_metrics.pkl',    None),  # SUPPRESSED
]


# -----------------------------------------------------------------------
# METRICS CONFIG
# -----------------------------------------------------------------------

def _load_metrics_config():
    if not os.path.exists(_METRICS_CONFIG_PATH):
        return {}
    try:
        with open(_METRICS_CONFIG_PATH, 'r') as f:
            raw = json.load(f)
    except Exception:
        return {}
    out = {}
    for section, section_cfg in raw.items():
        if section.startswith('_'):
            continue
        excluded = section_cfg.get('exclude', [])
        out[section] = {(pair[0], pair[1]) for pair in excluded if len(pair) == 2}
    return out


def _is_excluded(metrics_config, section, cat, flav):
    return (cat, flav) in metrics_config.get(section, set())


# -----------------------------------------------------------------------
# LOAD sphinxval METRICS PKLS
# -----------------------------------------------------------------------

def _metrics_dir():
    return '/home/m_sphinx/test_reqs/sphinxval/pushvivid_data/cumulative_metrics'


def _load_sphinxval_metrics(filename):
    path = os.path.join(_metrics_dir(), filename)
    if not os.path.exists(path):
        return pd.DataFrame()
    try:
        return pd.read_pickle(path)
    except Exception:
        return pd.DataFrame()


def _sphinxval_metric(metrics_df, model_name, energy_key, threshold_key, column):
    """Look up a metric for a specific model + energy channel + threshold.
    Normalizes the energy key so REleASE mismatch keys match the base channel."""
    if metrics_df.empty or 'Model' not in metrics_df.columns or column not in metrics_df.columns:
        return np.nan
    mask = (
        (metrics_df['Model'] == model_name) &
        (metrics_df['Energy Channel'].apply(_normalize_energy_key) == energy_key) &
        (metrics_df['Threshold'] == threshold_key)
    )
    sub = metrics_df[mask]
    if sub.empty:
        return np.nan
    val = pd.to_numeric(sub[column], errors='coerce').mean()
    return float(val) if pd.notna(val) else np.nan


# -----------------------------------------------------------------------
# ALL-TIME DELTA PKL
# -----------------------------------------------------------------------

def _load_previous_metrics():
    if os.path.exists(_DELTA_PKL):
        try:
            return pd.read_pickle(_DELTA_PKL)
        except Exception:
            pass
    return {}


def _save_metrics(metrics):
    pd.to_pickle(metrics, _DELTA_PKL)


# -----------------------------------------------------------------------
# FORMATTING
# -----------------------------------------------------------------------

def _fmt(value, precision=3):
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return 'N/A'
    return f'{value:.{precision}f}'


def _fmt_delta(current, previous, precision=3):
    cur_str = _fmt(current, precision)
    if previous is None or (isinstance(previous, float) and np.isnan(previous)):
        return cur_str
    if isinstance(current, float) and np.isnan(current):
        return cur_str
    delta = current - previous
    sign = '+' if delta >= 0 else ''
    return f'{cur_str} ({sign}{_fmt(delta, precision)})'


def _channel_label(energy_key, threshold_key):
    energy_str = manipulate_keys.convert_energy_key_to_string(energy_key)
    threshold_str = manipulate_keys.convert_threshold_key_to_string(threshold_key)
    return f'{energy_str}, {threshold_str}'


def _normalize_energy_key(energy_key):
    """Strip the mismatch suffix so REleASE mismatch keys group under
    their base channel."""
    return energy_key.split('_min.')[0]


# -----------------------------------------------------------------------
# PER-MODEL-PER-CHANNEL METRIC ASSEMBLY
# -----------------------------------------------------------------------

def _compute_model_metrics(df):
    """Return a dict mapping (cat, flav, energy_key, threshold_key) ->
    dict of metric_name -> value."""
    ac_df   = _load_sphinxval_metrics('all_clear_metrics.pkl')
    prob_df = _load_sphinxval_metrics('probability_metrics.pkl')
    flux_dfs = {label: _load_sphinxval_metrics(fname)
                for _, label, fname, _ in _FLUX_SECTIONS}

    results = {}
    for energy_key, threshold_key, _ in config.order.energy_channel_threshold_order:
        channel_mask = (
            df['Energy Channel Key'].apply(_normalize_energy_key) == energy_key) & (
            df['Threshold Key'] == threshold_key
        )
        channel_df = df[channel_mask]
        if channel_df.empty:
            continue

        for cat, cat_group in channel_df.groupby('Model Category'):
            for flav, _ in cat_group.groupby('Model Flavor'):
                key = (cat, flav, energy_key, threshold_key)
                model_name = f'{cat} {flav}'.strip()

                metrics = {}
                for label, col in _AC_METRICS:
                    metrics[label] = _sphinxval_metric(
                        ac_df, model_name, energy_key, threshold_key, col)
                for label, col in _PROB_METRICS:
                    metrics[label] = _sphinxval_metric(
                        prob_df, model_name, energy_key, threshold_key, col)
                for _, flux_label, _, _ in _FLUX_SECTIONS:
                    for label, col in _FLUX_METRICS:
                        metrics[f'{label} ({flux_label})'] = _sphinxval_metric(
                            flux_dfs[flux_label], model_name, energy_key, threshold_key, col)

                results[key] = metrics
    return results


# -----------------------------------------------------------------------
# TABLE BUILDING
# -----------------------------------------------------------------------

def _build_channel_metrics_table(current, previous, metric_names,
                                  section_key, energy_key, threshold_key,
                                  headers, metrics_config):
    """Build one HTML table for a single energy/threshold channel."""
    table_data = []
    for (cat, flav, ekey, tkey), metrics in sorted(current.items()):
        if ekey != energy_key or tkey != threshold_key:
            continue
        if _is_excluded(metrics_config, section_key, cat, flav):
            continue
        prev_metrics = previous.get((cat, flav, ekey, tkey), {})
        row = [cat, flav]
        for m in metric_names:
            cur_val = metrics.get(m, np.nan)
            prev_val = prev_metrics.get(m, np.nan)
            row.append(_fmt_delta(cur_val, prev_val))
        table_data.append(row)
    if not table_data:
        return ''
    buf = io.StringIO()
    buf.write(build_html.build_table(headers, table_data))
    return buf.getvalue()


def _build_metrics_section_tables(current, previous, metric_names,
                                   section_key, title, headers, metrics_config):
    """Build a full metrics section with one sub-table per channel."""
    buf = io.StringIO()
    buf.write(build_html.build_paragraph_title(title))
    any_table = False
    for energy_key, threshold_key, _ in config.order.energy_channel_threshold_order:
        table_html = _build_channel_metrics_table(
            current, previous, metric_names, section_key,
            energy_key, threshold_key, headers, metrics_config)
        if table_html:
            label = _channel_label(energy_key, threshold_key)
            buf.write(build_html.build_paragraph_title(label, sublevel=1))
            buf.write(table_html)
            any_table = True
    if not any_table:
        buf.write(build_html.build_regular_text('No data available.'))
    return buf.getvalue()


# -----------------------------------------------------------------------
# PUBLIC ENTRY POINT
# -----------------------------------------------------------------------

def build_metrics_section(df):
    current = _compute_model_metrics(df)
    previous = _load_previous_metrics()
    _save_metrics(current)
    metrics_config = _load_metrics_config()

    buf = io.StringIO()
    buf.write(build_html.build_section_title('Metrics Summary'))
    buf.write(build_html.build_regular_text(
        'Values shown as X (+/-Y), where X is the all-time metric and '
        'Y is the change since the previous report. All metrics are '
        'taken directly from sphinxval.'))

    # METRICS LEGEND
    legend_headers = ['Abbreviation', 'Full Name', 'Description']
    legend_data = [
        ['Hit Rate',     'Hit Rate (Probability of Detection)',  'Fraction of observed SEP events that were correctly predicted. Range: [0, 1]; higher is better.'],
        ['FAR',          'False Alarm Ratio',                    'Fraction of predicted SEP events that did not occur. Range: [0, 1]; lower is better.'],
        ['FAER',         'False Alarm Event Ratio',              'Number of false alarms divided by number of observed SEP events. Range: [0, &infin;); lower is better.'],
        ['HSS',          'Heidke Skill Score',                   'Skill relative to random chance. Range: (-&infin;, 1]; higher is better; 0 = no skill.'],
        ['TSS',          'True Skill Statistic',                 'Hit Rate minus False Alarm Rate. Range: [-1, 1]; higher is better; 0 = no skill.'],
        ['Brier Score',  'Brier Score',                          'Mean squared error of probability forecasts. Range: [0, 1]; lower is better.'],
        ['AUC',          'Area Under ROC Curve',                 'Ability to discriminate between events and non-events. Range: [0, 1]; higher is better; 0.5 = no skill.'],
        ['MLE',          'Median Log Error',                     'Median of log&#8321;&#8320;(predicted/observed) peak flux. 0 = perfect; positive = overprediction; negative = underprediction.'],
        ['WF2',          'Within Factor of 2',                   'Percentage of forecasts within a factor of 2 of the observed peak flux. Higher is better.'],
        ['WF10',         'Within Factor of 10',                  'Percentage of forecasts within an order of magnitude of the observed peak flux. Higher is better.'],
    ]
    buf.write(build_html.build_table(legend_headers, legend_data))
    buf.write(build_html.build_divider())

    ac_metrics = ['Hit Rate', 'FAR', 'FAER', 'HSS', 'TSS']
    ac_headers = ['Model Category', 'Model Flavor'] + ac_metrics
    buf.write(_build_metrics_section_tables(
        current, previous, ac_metrics, _SECTION_ALL_CLEAR,
        'All Clear Metrics', ac_headers, metrics_config))

    prob_metrics = ['Brier Score', 'AUC']
    prob_headers = ['Model Category', 'Model Flavor'] + prob_metrics
    buf.write(_build_metrics_section_tables(
        current, previous, prob_metrics, _SECTION_PROBABILITY,
        'Probability Metrics', prob_headers, metrics_config))

    for section_key, flux_label, _, display_title in _FLUX_SECTIONS:
        if display_title is None:
            continue  # SUPPRESSED SECTION
        flux_metrics = [f'MLE ({flux_label})', f'WF2 ({flux_label})', f'WF10 ({flux_label})']
        flux_headers = ['Model Category', 'Model Flavor', 'MLE', 'WF2', 'WF10']
        buf.write(_build_metrics_section_tables(
            current, previous, flux_metrics, section_key,
            display_title, flux_headers, metrics_config))

    buf.write(build_html.build_divider())
    return buf.getvalue()
