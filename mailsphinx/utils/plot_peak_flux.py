from ..utils import build_html
from ..utils import config
from ..utils import filter_objects

import math
import os
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.lines
import matplotlib.patches
import matplotlib.pyplot as plt

plt.rcParams['font.family'] = config.plot.font
plt.rcParams['font.size'] = config.plot.fontsize

# FONT SIZE SPECIFIC TO THE PEAK FLUX SCATTER PLOTS AND THEIR SHARED
# LEGEND, DELIBERATELY SMALLER THAN THE GLOBAL config.plot.fontsize (16)
# USED BY EVERY OTHER PLOT TYPE (contingency, advanced warning,
# probability). SCOPED VIA plt.rc_context() AROUND JUST THESE TWO
# FUNCTIONS' PLOTTING CODE SO IT DOES NOT AFFECT ANY OTHER PLOT OR
# CHANGE THE GLOBAL rcParams STATE.
PEAK_FLUX_FONTSIZE = 10
PEAK_FLUX_DPI = config.image.dpi * 2


# DATA TYPE DEFINITIONS: (display_name, pred_col, obs_col, marker_key)
ONSET_PEAK = (
    'Onset Peak',
    'Predicted SEP Peak Intensity (Onset Peak)',
    'Observed SEP Peak Intensity (Onset Peak)',
    'Onset Peak',
)
MAX_FLUX = (
    'Max Flux',
    'Predicted SEP Peak Intensity Max (Max Flux)',
    'Observed SEP Peak Intensity Max (Max Flux)',
    'Max Flux',
)


def release_selections_dir():
    """WHERE run_sphinx.sh ACCUMULATES THE REleASE _mm_Max SELECTION CSVs:
    <CODE_DIR>/sphinxval/pushvivid_data/cumulative_release_selections.
    RESOLVED THE SAME WAY build_metrics._metrics_dir() RESOLVES cumulative_metrics
    (pipeline_config.CODE_DIR), FALLING BACK TO THE CODE DIRECTORY FOUR LEVELS ABOVE
    THIS FILE (<CODE_DIR>/mailsphinx/mailsphinx/utils/plot_peak_flux.py). THE OLD
    CODE WENT ONLY THREE LEVELS UP (<CODE_DIR>/mailsphinx/pushvivid_data/...), A
    DIRECTORY THAT DOES NOT EXIST, SO NO REleASE POINT WAS EVER PLOTTED."""
    import sys as _sys
    try:
        _sys.path.insert(0, '/data/SPHINX/code')
        import pipeline_config as _pc
        code_dir = _pc.CODE_DIR
    except Exception:
        code_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__)))))
    return os.path.join(code_dir, 'sphinxval', 'pushvivid_data', 'cumulative_release_selections')


def _release_file_prefix(marker_key):
    # peak_intensity_selections_*_mm_Max.csv     -> ONSET PEAK (OBS = ONSET PEAK)
    # peak_intensity_max_selections_*_mm_Max.csv -> MAX FLUX   (OBS = MAX FLUX)
    return 'peak_intensity_selections_' if marker_key == 'Onset Peak' else 'peak_intensity_max_selections_'


def load_release_selections(marker_key):
    """READ AND CONCATENATE EVERY REleASE SELECTION CSV FOR ONE DATA TYPE (ALL CHANNELS,
    ALL TIME). FILTER THE RESULT WITH filter_release_selections() BEFORE PLOTTING."""
    release_dir = release_selections_dir()
    prefix = _release_file_prefix(marker_key)
    if not os.path.isdir(release_dir):
        # SAY SO INSTEAD OF SILENTLY PLOTTING NO REleASE POINTS
        print(f'WARNING: REleASE selections directory not found: {release_dir}')
        return pd.DataFrame()
    frames = []
    for fname in sorted(os.listdir(release_dir)):
        if fname.startswith(prefix) and fname.endswith('_mm_Max.csv'):
            try:
                frames.append(pd.read_csv(os.path.join(release_dir, fname)))
            except Exception as e:
                print(f'WARNING: could not read {fname}: {e}')
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def filter_release_selections(release_df, energy_key, threshold_key, start=None, end=None):
    """KEEP ONLY ROWS FOR ONE CHANNEL (OBSERVED Energy Channel Key, MISMATCH SUFFIX
    STRIPPED AS IN build_model._norm_energy_key, AND Threshold Key), AND, IF GIVEN, WITH
    start <= Prediction Window Start < end. THE CSVs HAVE NO Forecast Issue Time (WHAT
    THE REST OF THE EMAIL USES FOR "THIS PERIOD"), SO Prediction Window Start STANDS IN."""
    if release_df.empty:
        return release_df
    keep = (release_df['Energy Channel Key'].astype(str).str.split('_min.', regex=False).str[0].eq(energy_key) &
            release_df['Threshold Key'].astype(str).eq(threshold_key))
    if start is not None or end is not None:
        pws = pd.to_datetime(release_df['Prediction Window Start'], utc=True, errors='coerce')
        if start is not None:
            keep &= pws >= pd.Timestamp(start)
        if end is not None:
            keep &= pws < pd.Timestamp(end)
    return release_df[keep]


def build_category_colors(df):
    """ONE FIXED Model Category -> COLOR MAP FOR ALL PEAK FLUX PLOTS AND THEIR LEGENDS.
    BUILT ONCE FROM THE FULL df SO A CATEGORY HAS THE SAME COLOR IN EVERY CHANNEL,
    EVERY PERIOD AND THE LEGEND. CATEGORIES NOT IN df (E.G. A REleASE NAME FROM THE
    SELECTION CSVs) ARE ADDED ON FIRST USE BY _category_color() WITH THE NEXT INDEX."""
    cats = sorted(df['Model Category'].dropna().unique())
    return {cat: config.color.color_cycle[i % len(config.color.color_cycle)]
            for i, cat in enumerate(cats)}


def _category_color(category_colors, cat):
    # ADD UNKNOWN CATEGORIES AT THE NEXT INDEX INSTEAD OF SILENTLY REUSING INDEX 0
    if cat not in category_colors:
        n = len(category_colors)
        category_colors[cat] = config.color.color_cycle[n % len(config.color.color_cycle)]
    return category_colors[cat]


def plot_peak_flux_single(energy_channel_string, threshold_flux_string, df,
                          save, threshold_flux, data_type_def,
                          period_label, axis_min=None, axis_max=None,
                          convert_image_to_base64=False,
                          category_colors=None, plotted_categories=None,
                          release_df=None):
    """Plot predicted vs. observed peak flux for a single data type.
    NO LEGEND IS DRAWN so the plotting area is always a uniform square.
    Call build_peak_flux_legend() separately to produce a shared legend.

    Parameters
    ----------
    axis_min, axis_max : float or None
        Fixed axis limits in pfu. If None, defaults to ±3/+4 decades
        centered on threshold_flux.
    release_df : DataFrame or None
        REleASE SELECTION ROWS ALREADY FILTERED TO THIS CHANNEL AND PERIOD
        (load_release_selections + filter_release_selections). None = NO REleASE POINTS.
    """
    display_name, pred_col, obs_col, marker_key = data_type_def

    # COMPUTE AXIS LIMITS IF NOT EXPLICITLY PROVIDED
    if axis_min is None or axis_max is None:
        log_thresh = math.log10(threshold_flux)
        axis_min = 10 ** (log_thresh - 3.0)
        axis_max = 10 ** (log_thresh + 4.0)

    # ax.set_aspect('equal') ENFORCES A SQUARE PLOTTING AREA INDEPENDENT
    # OF FIGURE SIZE. tight_layout WITH NO LEGEND KEEPS IT CONSISTENT.
    with plt.rc_context({'font.size': PEAK_FLUX_FONTSIZE}):
        fig, ax = plt.subplots(1, 1, figsize=(config.image.peak_flux_width,
                                              config.image.peak_flux_height))

        # REleASE POINTS COME FROM THE CUMULATIVE _mm_Max SELECTION CSVs (PASSED IN AS
        # release_df, ALREADY FILTERED). BOTH FILE TYPES USE THE ONSET PEAK PREDICTION.
        release_pred_col = 'Predicted SEP Peak Intensity (Onset Peak)'
        if marker_key == 'Onset Peak':
            release_obs_col = 'Observed SEP Peak Intensity (Onset Peak)'
        else:
            release_obs_col = 'Observed SEP Peak Intensity Max (Max Flux)'
        if release_df is None:
            release_df = pd.DataFrame()

        # FILTER df TO NON-REleASE MODELS ONLY FOR STANDARD COLUMN PLOTTING
        is_release = df['Model'].str.contains('REleASE', case=False, na=False)
        non_release_df = df[~is_release]

        # SHARED COLOR MAP (SEE build_category_colors); FALL BACK TO ONE BUILT FROM THIS df
        if category_colors is None:
            category_colors = build_category_colors(df)
        handles = []
        has_data = False

        def _scatter(source_df, use_pred_col, use_obs_col, is_release_src=False):
            nonlocal has_data
            group_col = 'Model Category' if not is_release_src else 'Model'
            if group_col not in source_df.columns:
                return
            for group_key, group in source_df.groupby(group_col):
                grp = group[[use_pred_col, use_obs_col]].dropna()
                grp = grp[(grp[use_pred_col] > 0) & (grp[use_obs_col] > 0)]
                if len(grp) == 0:
                    continue
                # FOR REleASE, DERIVE CATEGORY FROM MODEL NAME
                if is_release_src:
                    from ..utils import filter_objects as _fo
                    cat, _ = _fo.extract_common_substring(group_key)
                else:
                    cat = group_key
                color = _category_color(category_colors, cat)
                # RECORD WHAT WAS ACTUALLY DRAWN SO THE LEGEND LISTS ONLY THESE
                if plotted_categories is not None:
                    plotted_categories.add(cat)
                ax.scatter(grp[use_obs_col], grp[use_pred_col],
                           s=config.plot.marker_size, color=color,
                           marker=config.shape.associations[marker_key],
                           facecolors='none', zorder=2)
                if not any(h.get_label() == cat for h in handles):
                    handles.append(matplotlib.patches.Patch(color=color, label=cat))
                has_data = True

        _scatter(non_release_df, pred_col, obs_col)
        if not release_df.empty:
            _scatter(release_df, release_pred_col, release_obs_col, is_release_src=True)

        if not has_data:
            ax.text(0.5, 0.5, 'No data', transform=ax.transAxes,
                    ha='center', va='center', fontsize=12, color='gray')

        log_thresh = math.log10(threshold_flux)
        base_title = energy_channel_string + ', ' + threshold_flux_string
        color_key = base_title.replace('> ', '>=') + ' Event'

        ax.plot([axis_min, axis_max], [axis_min, axis_max],
                color='black', linestyle='--', zorder=0)
        ax.plot([threshold_flux, threshold_flux], [axis_min, axis_max],
                color=config.color.associations[color_key], linestyle='solid', zorder=0)
        ax.plot([axis_min, axis_max], [threshold_flux, threshold_flux],
                color=config.color.associations[color_key], linestyle='solid', zorder=0)

        ax.grid(True, which='major', linestyle='--', linewidth=0.5, alpha=0.7)
        ax.set_title(f'{base_title} — {display_name} ({period_label})')
        ax.set_xlabel('Observed Peak Flux [pfu]')
        ax.set_ylabel('Predicted Peak Flux [pfu]')
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.set_xlim([axis_min, axis_max])
        ax.set_ylim([axis_min, axis_max])
        ax.set_aspect('equal', adjustable='box')

        # SHOW A TICK LABEL AT EVERY ORDER OF MAGNITUDE
        import matplotlib.ticker as mticker
        ax.xaxis.set_major_locator(mticker.LogLocator(base=10, numticks=20))
        ax.yaxis.set_major_locator(mticker.LogLocator(base=10, numticks=20))
        ax.xaxis.set_major_formatter(mticker.LogFormatterSciNotation(base=10))
        ax.yaxis.set_major_formatter(mticker.LogFormatterSciNotation(base=10))
        ax.xaxis.set_minor_locator(mticker.LogLocator(base=10, subs='auto', numticks=20))
        ax.yaxis.set_minor_locator(mticker.LogLocator(base=10, subs='auto', numticks=20))
        ax.xaxis.set_minor_formatter(mticker.NullFormatter())
        ax.yaxis.set_minor_formatter(mticker.NullFormatter())

        plt.tight_layout()
        plt.savefig(save, dpi=PEAK_FLUX_DPI, bbox_inches='tight')
        plt.close()

    return True, build_html.build_image(save, write_as_base64=convert_image_to_base64, native_size=True)


def build_peak_flux_legend(df, save, convert_image_to_base64=False,
                           category_colors=None, categories=None):
    """Build a standalone legend image for the peak flux plots.
    WITH categories GIVEN (THE ONES ACTUALLY PLOTTED), ONLY THOSE ARE LISTED;
    OTHERWISE EVERY Model Category IN df. COLORS COME FROM category_colors SO
    THEY MATCH THE PLOTS."""
    if category_colors is None:
        category_colors = build_category_colors(df)
    if categories is None:
        categories = df['Model Category'].dropna().unique()
    categories = sorted(categories)
    if not categories:
        return ''

    handles = [
        matplotlib.patches.Patch(color=_category_color(category_colors, cat), label=cat)
        for cat in categories
    ]

    # USE 2 COLUMNS TO KEEP THE LEGEND COMPACT
    ncol = 2
    nrows = math.ceil(len(handles) / ncol)
    fig_width = 4.0
    fig_height = max(0.5, nrows * 0.28 + 0.3)

    with plt.rc_context({'font.size': PEAK_FLUX_FONTSIZE}):
        fig, ax = plt.subplots(figsize=(fig_width, fig_height))
        ax.axis('off')
        ax.legend(handles=handles, loc='center', framealpha=config.plot.opacity,
                  fontsize='small', ncol=ncol, columnspacing=1.0, handlelength=1.5)
        plt.tight_layout()
        plt.savefig(save, dpi=PEAK_FLUX_DPI, bbox_inches='tight')
        plt.close()

    return build_html.build_image(save, write_as_base64=convert_image_to_base64, native_size=True)

