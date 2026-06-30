"""Display per-model validation metrics in the MailSPHINX email.

All metrics are read directly from sphinxval's own metrics pkl files
(all_clear_metrics.pkl, probability_metrics.pkl, peak_intensity_metrics.pkl,
peak_intensity_max_metrics.pkl, max_flux_in_pred_win_metrics.pkl), which
are copied to a persistent location by run_sphinx.sh each month since
SPHINX validates against the full cumulative history. MailSPHINX performs
no metric computation of its own — this avoids duplicating sphinxval's
formulas and any risk of disagreement between the two.

The all-time values from the previous run are stored in
all_time_metrics.pkl so the +/-Y change since the last report
can be shown alongside each value.

Sections:
    All Clear:   Hit Rate, FAR, FAER, HSS, TSS
    Probability: Brier Score, AUC
    Max Flux:    Median Log Error, Within Factor 2, Within Factor 10
                 (computed for onset peak, max flux, and max flux in
                 prediction window separately)
"""

import io
import os

import numpy as np
import pandas as pd

from ..utils import build_html
from ..utils import config


# -----------------------------------------------------------------------
# PATHS
# -----------------------------------------------------------------------

_DELTA_PKL = config.path.all_time_metrics


# -----------------------------------------------------------------------
# SPHINXVAL METRICS FILE COLUMN NAME MAPPING
# -----------------------------------------------------------------------

# (display_name, sphinxval_column_name)
_AC_METRICS = [
    ('Hit Rate', 'Hit Rate'),
    ('FAR',      'False Alarm Ratio'),
    ('FAER',     'False Alarm Event Ratio'),
    ('HSS',      'Heidke Skill Score'),
    ('TSS',      'True Skill Statistic'),
]
_PROB_METRICS = [
    ('Brier Score', 'Brier Score'),
    ('AUC',          'Area Under ROC Curve'),
]
_FLUX_METRICS = [
    ('MLE',  'Median Log Error (MedLE)'),
    ('WF2',  'Percentage within a factor of 2 (%)'),
    ('WF10', 'Percentage within an Order of Magnitude (%)'),
]

# sphinxval METRICS PKL FILENAMES KEYED BY FLUX LABEL
_FLUX_METRICS_FILES = {
    'Onset Peak':              'peak_intensity_metrics.pkl',
    'Max Flux':                'peak_intensity_max_metrics.pkl',
    'Max Flux in Pred Window': 'max_flux_in_pred_win_metrics.pkl',
}


# -----------------------------------------------------------------------
# LOAD SPHINXVAL'S OWN METRICS PKLS
# -----------------------------------------------------------------------

def _metrics_dir():
    # ABSOLUTE PATH: WHERE run_sphinx.sh COPIES sphinxval's METRICS PKLS
    # EACH MONTH (SEE cumulative_metrics_directory IN run_sphinx.sh)
    return '/home/m_sphinx/test_reqs/sphinxval/pushvivid_data/cumulative_metrics'


def _load_sphinxval_metrics(filename):
    """Load one of sphinxval's metrics pkls from the persistent cumulative
    location. Returns an empty dataframe if not found (e.g. first run)."""
    path = os.path.join(_metrics_dir(), filename)
    if not os.path.exists(path):
        return pd.DataFrame()
    try:
        return pd.read_pickle(path)
    except Exception:
        return pd.DataFrame()


def _sphinxval_metric_for_model(metrics_df, model_name, column):
    """Look up a single metric value for a given full model name
    (e.g. 'MAG4 LOS_FEr') from a sphinxval metrics dataframe. If the
    model appears with multiple energy/threshold rows, returns the
    mean across rows."""
    if metrics_df.empty or 'Model' not in metrics_df.columns or column not in metrics_df.columns:
        return np.nan
    sub = metrics_df[metrics_df['Model'] == model_name]
    if sub.empty:
        return np.nan
    val = pd.to_numeric(sub[column], errors='coerce').mean()
    return float(val) if pd.notna(val) else np.nan


# -----------------------------------------------------------------------
# ALL-TIME DELTA PKL LOAD / SAVE
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


# -----------------------------------------------------------------------
# PER-MODEL METRIC ASSEMBLY
# -----------------------------------------------------------------------

def _compute_model_metrics(df):
    """Return a dict mapping (model_category, model_flavor) -> dict of
    metric_name -> value, pulled entirely from sphinxval's own metrics
    pkls. df is used only to enumerate which (category, flavor) pairs
    are present in the current dataframe."""
    ac_df = _load_sphinxval_metrics('all_clear_metrics.pkl')
    prob_df = _load_sphinxval_metrics('probability_metrics.pkl')
    flux_dfs = {label: _load_sphinxval_metrics(fname)
                for label, fname in _FLUX_METRICS_FILES.items()}

    results = {}
    for cat, cat_group in df.groupby('Model Category'):
        for flav, _ in cat_group.groupby('Model Flavor'):
            key = (cat, flav)
            model_name = f'{cat} {flav}'.strip()

            metrics = {}
            for label, col in _AC_METRICS:
                metrics[label] = _sphinxval_metric_for_model(ac_df, model_name, col)

            for label, col in _PROB_METRICS:
                metrics[label] = _sphinxval_metric_for_model(prob_df, model_name, col)

            for flux_label in _FLUX_METRICS_FILES:
                for label, col in _FLUX_METRICS:
                    metrics[f'{label} ({flux_label})'] = _sphinxval_metric_for_model(
                        flux_dfs[flux_label], model_name, col)

            results[key] = metrics
    return results


# -----------------------------------------------------------------------
# TABLE BUILDING
# -----------------------------------------------------------------------

def _build_metrics_table(current, previous, metric_names, title, headers):
    buf = io.StringIO()
    buf.write(build_html.build_paragraph_title(title))
    table_data = []
    for (cat, flav), metrics in sorted(current.items()):
        prev_metrics = previous.get((cat, flav), {})
        row = [cat, flav]
        for m in metric_names:
            cur_val = metrics.get(m, np.nan)
            prev_val = prev_metrics.get(m, np.nan)
            row.append(_fmt_delta(cur_val, prev_val))
        table_data.append(row)
    if table_data:
        buf.write(build_html.build_table(headers, table_data))
    else:
        buf.write(build_html.build_regular_text('No data available.'))
    return buf.getvalue()


# -----------------------------------------------------------------------
# PUBLIC ENTRY POINT
# -----------------------------------------------------------------------

def build_metrics_section(df):
    """Assemble metrics from sphinxval's metrics pkls (plus FAER/WF10
    computed locally), update the all-time delta pkl, and return HTML."""
    current = _compute_model_metrics(df)
    previous = _load_previous_metrics()
    _save_metrics(current)

    buf = io.StringIO()
    buf.write(build_html.build_section_title('Metrics Summary'))
    buf.write(build_html.build_regular_text(
        'Values shown as X (+/-Y), where X is the all-time metric and '
        'Y is the change since the previous report. All metrics are '
        'taken directly from sphinxval. '
        'MLE = Median Log Error. WF2/WF10 = percentage of forecasts '
        'within a factor of 2/10 (order of magnitude) of observed.'))

    ac_metrics = ['Hit Rate', 'FAR', 'FAER', 'HSS', 'TSS']
    ac_headers = ['Model Category', 'Model Flavor'] + ac_metrics
    buf.write(_build_metrics_table(
        current, previous, ac_metrics, 'All Clear Metrics', ac_headers))

    prob_metrics = ['Brier Score', 'AUC']
    prob_headers = ['Model Category', 'Model Flavor'] + prob_metrics
    buf.write(_build_metrics_table(
        current, previous, prob_metrics, 'Probability Metrics', prob_headers))

    for label in _FLUX_METRICS_FILES:
        flux_metrics = [f'MLE ({label})', f'WF2 ({label})', f'WF10 ({label})']
        flux_headers = ['Model Category', 'Model Flavor', 'MLE', 'WF2', 'WF10']
        buf.write(_build_metrics_table(
            current, previous, flux_metrics,
            f'Max Flux Metrics ({label})', flux_headers))

    buf.write(build_html.build_divider())
    return buf.getvalue()
