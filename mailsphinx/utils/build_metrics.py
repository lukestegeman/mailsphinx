"""
Compute and display per-model validation metrics in the MailSPHINX email.

Metrics are computed over all time (X) and the change since the last
run (+/-Y) is shown alongside. The all-time values from the previous
run are stored in all_time_metrics.pkl and updated each run.

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
from sklearn.metrics import roc_auc_score

from ..utils import build_html
from ..utils import config


# -----------------------------------------------------------------------
# PATHS
# -----------------------------------------------------------------------

_METRICS_PKL = config.path.all_time_metrics


# -----------------------------------------------------------------------
# METRIC COMPUTATION HELPERS
# -----------------------------------------------------------------------

def _contingency_counts(df):
    """Return (H, M, FA, CN) for a dataframe subset."""
    h  = ((df['Observed SEP All Clear'] == False) & (df['Predicted SEP All Clear'] == False)).sum()
    m  = ((df['Observed SEP All Clear'] == False) & (df['Predicted SEP All Clear'] == True )).sum()
    fa = ((df['Observed SEP All Clear'] == True ) & (df['Predicted SEP All Clear'] == False)).sum()
    cn = ((df['Observed SEP All Clear'] == True ) & (df['Predicted SEP All Clear'] == True )).sum()
    return int(h), int(m), int(fa), int(cn)


def _hit_rate(h, m):
    return h / (h + m) if (h + m) > 0 else np.nan


def _far(h, fa):
    return fa / (fa + h) if (fa + h) > 0 else np.nan


def _faer(fa, h, m):
    return fa / (h + m) if (h + m) > 0 else np.nan


def _hss(h, m, fa, cn):
    denom = (h + m) * (m + cn) + (h + fa) * (fa + cn)
    return 2 * (h * cn - fa * m) / denom if denom > 0 else np.nan


def _tss(h, m, fa, cn):
    pod = h / (h + m) if (h + m) > 0 else np.nan
    pofd = fa / (fa + cn) if (fa + cn) > 0 else np.nan
    if np.isnan(pod) or np.isnan(pofd):
        return np.nan
    return pod - pofd


def _brier_score(df):
    sub = df[df['Predicted SEP Probability'].notna() &
             df['Observed SEP Probability'].notna()]
    if len(sub) == 0:
        return np.nan
    return float(np.mean((sub['Predicted SEP Probability'] -
                          sub['Observed SEP Probability']) ** 2))


def _auc(df):
    sub = df[df['Predicted SEP Probability'].notna() &
             df['Observed SEP Probability'].notna()]
    if len(sub) == 0 or sub['Observed SEP Probability'].nunique() < 2:
        return np.nan
    try:
        return float(roc_auc_score(sub['Observed SEP Probability'],
                                   sub['Predicted SEP Probability']))
    except Exception:
        return np.nan


def _flux_metrics(pred, obs):
    """Compute median log error, within-factor-2, and within-factor-10
    for a pair of predicted/observed flux Series. Both must be > 0."""
    mask = pred.notna() & obs.notna() & (pred > 0) & (obs > 0)
    sub_pred = pred[mask]
    sub_obs = obs[mask]
    n = len(sub_pred)
    if n == 0:
        return np.nan, np.nan, np.nan, 0
    ratio = sub_pred / sub_obs
    log_error = float(np.median(np.log10(ratio)))
    wf2 = float((ratio.between(0.5, 2.0)).sum() / n)
    wf10 = float((ratio.between(0.1, 10.0)).sum() / n)
    return log_error, wf2, wf10, n


# -----------------------------------------------------------------------
# PER-MODEL METRIC COMPUTATION
# -----------------------------------------------------------------------

def _compute_model_metrics(df):
    """Return a dict mapping (model_category, model_flavor) →
    dict of metric_name → value, computed over the full df."""
    results = {}
    for cat, cat_group in df.groupby('Model Category'):
        for flav, sub in cat_group.groupby('Model Flavor'):
            key = (cat, flav)
            h, m, fa, cn = _contingency_counts(sub)
            mle_op, wf2_op, wf10_op, n_op = _flux_metrics(
                sub['Predicted SEP Peak Intensity (Onset Peak)'],
                sub['Observed SEP Peak Intensity (Onset Peak)'])
            mle_mf, wf2_mf, wf10_mf, n_mf = _flux_metrics(
                sub['Predicted SEP Peak Intensity Max (Max Flux)'],
                sub['Observed SEP Peak Intensity Max (Max Flux)'])
            mle_mw, wf2_mw, wf10_mw, n_mw = _flux_metrics(
                sub['Predicted SEP Peak Intensity Max (Max Flux)'],
                sub['Observed Max Flux in Prediction Window'])
            results[key] = {
                # ALL CLEAR
                'Hit Rate':  _hit_rate(h, m),
                'FAR':       _far(h, fa),
                'FAER':      _faer(fa, h, m),
                'HSS':       _hss(h, m, fa, cn),
                'TSS':       _tss(h, m, fa, cn),
                # PROBABILITY
                'Brier Score': _brier_score(sub),
                'AUC':         _auc(sub),
                # MAX FLUX — ONSET PEAK
                'MLE (Onset Peak)':   mle_op,
                'WF2 (Onset Peak)':   wf2_op,
                'WF10 (Onset Peak)':  wf10_op,
                'N (Onset Peak)':     n_op,
                # MAX FLUX — MAX FLUX
                'MLE (Max Flux)':     mle_mf,
                'WF2 (Max Flux)':     wf2_mf,
                'WF10 (Max Flux)':    wf10_mf,
                'N (Max Flux)':       n_mf,
                # MAX FLUX — MAX FLUX IN PREDICTION WINDOW
                'MLE (Max Flux in Pred Win)':  mle_mw,
                'WF2 (Max Flux in Pred Win)':  wf2_mw,
                'WF10 (Max Flux in Pred Win)': wf10_mw,
                'N (Max Flux in Pred Win)':    n_mw,
            }
    return results


# -----------------------------------------------------------------------
# ALL-TIME PKL LOAD / SAVE
# -----------------------------------------------------------------------

def _load_previous_metrics():
    """Load the previous run's all-time metrics, or return empty dict."""
    if os.path.exists(_METRICS_PKL):
        try:
            return pd.read_pickle(_METRICS_PKL)
        except Exception:
            pass
    return {}


def _save_metrics(metrics):
    pd.to_pickle(metrics, _METRICS_PKL)


# -----------------------------------------------------------------------
# FORMATTING
# -----------------------------------------------------------------------

def _fmt(value, precision=3):
    """Format a metric value for display."""
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return 'N/A'
    if isinstance(value, int):
        return str(value)
    return f'{value:.{precision}f}'


def _fmt_delta(current, previous, precision=3):
    """Format current value with delta from previous run as X (+/-Y)."""
    cur_str = _fmt(current, precision)
    if previous is None or (isinstance(previous, float) and np.isnan(previous)):
        return cur_str
    if isinstance(current, float) and np.isnan(current):
        return cur_str
    delta = current - previous
    sign = '+' if delta >= 0 else ''
    return f'{cur_str} ({sign}{_fmt(delta, precision)})'


def _build_metrics_table(current, previous, metric_names, title, headers):
    """Build an HTML table for a set of metrics across all models."""
    buf = io.StringIO()
    buf.write(build_html.build_paragraph_title(title))
    table_data = []
    for (cat, flav), metrics in sorted(current.items()):
        prev_metrics = previous.get((cat, flav), {})
        row = [cat, flav]
        for m in metric_names:
            cur_val = metrics.get(m, np.nan)
            prev_val = prev_metrics.get(m, np.nan)
            # N (SAMPLE SIZE) COLUMNS SHOWN WITHOUT DELTA
            if m.startswith('N '):
                row.append(_fmt(cur_val, 0))
            else:
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
    """Compute metrics, update the all-time pkl, and return HTML."""
    current = _compute_model_metrics(df)
    previous = _load_previous_metrics()
    _save_metrics(current)

    buf = io.StringIO()
    buf.write(build_html.build_section_title('Metrics Summary'))
    buf.write(build_html.build_regular_text(
        'Values shown as X (+/-Y), where X is the all-time metric and '
        'Y is the change since the previous report. '
        'MLE = Median Log Error (log10(pred/obs)). '
        'WF2/WF10 = fraction of forecasts within a factor of 2/10 of observed. '
        'N = number of paired samples used.'))

    # ALL CLEAR METRICS
    ac_metrics = ['Hit Rate', 'FAR', 'FAER', 'HSS', 'TSS']
    ac_headers = ['Model Category', 'Model Flavor'] + ac_metrics
    buf.write(_build_metrics_table(
        current, previous, ac_metrics,
        'All Clear Metrics', ac_headers))

    # PROBABILITY METRICS
    prob_metrics = ['Brier Score', 'AUC']
    prob_headers = ['Model Category', 'Model Flavor'] + prob_metrics
    buf.write(_build_metrics_table(
        current, previous, prob_metrics,
        'Probability Metrics', prob_headers))

    # MAX FLUX METRICS — THREE OBSERVATION TYPES
    for label, suffix in [
        ('Onset Peak',               'Onset Peak'),
        ('Max Flux',                 'Max Flux'),
        ('Max Flux in Pred Window',  'Max Flux in Pred Win'),
    ]:
        flux_metrics = [
            f'MLE ({suffix})', f'WF2 ({suffix})',
            f'WF10 ({suffix})', f'N ({suffix})',
        ]
        flux_headers = ['Model Category', 'Model Flavor',
                        'MLE', 'WF2', 'WF10', 'N']
        buf.write(_build_metrics_table(
            current, previous, flux_metrics,
            f'Max Flux Metrics ({label})', flux_headers))

    buf.write(build_html.build_divider())
    return buf.getvalue()
