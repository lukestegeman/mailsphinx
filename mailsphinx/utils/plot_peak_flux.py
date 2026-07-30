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


def plot_peak_flux_single(energy_channel_string, threshold_flux_string, df,
                          save, threshold_flux, data_type_def,
                          period_label, axis_min=None, axis_max=None,
                          convert_image_to_base64=False):
    """Plot predicted vs. observed peak flux for a single data type.
    NO LEGEND IS DRAWN so the plotting area is always a uniform square.
    Call build_peak_flux_legend() separately to produce a shared legend.

    Parameters
    ----------
    axis_min, axis_max : float or None
        Fixed axis limits in pfu. If None, defaults to ±3/+4 decades
        centered on threshold_flux.
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

        # FOR REleASE MODELS, READ FROM CUMULATIVE _mm_Max SELECTION CSV FILES
        # ACCUMULATED BY run_sphinx.sh. THESE ARE THE AUTHORITATIVE SOURCE FOR
        # PREDICTED VS. OBSERVED PEAK FLUX PAIRS FROM THE _mm_Max SELECTIONS FILES.
        # peak_intensity_selections_*_mm_Max.csv  → ONSET PEAK (obs = onset peak)
        # peak_intensity_max_selections_*_mm_Max.csv → MAX FLUX  (obs = max flux)
        RELEASE_DIR = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(
                os.path.abspath(__file__)))),
            'pushvivid_data', 'cumulative_release_selections'
        )
        # DETERMINE WHICH SELECTIONS FILE TYPE TO USE BASED ON DATA TYPE
        if marker_key == 'Onset Peak':
            release_file_prefix = 'peak_intensity_selections_'
            release_pred_col = 'Predicted SEP Peak Intensity (Onset Peak)'
            release_obs_col  = 'Observed SEP Peak Intensity (Onset Peak)'
        else:
            release_file_prefix = 'peak_intensity_max_selections_'
            release_pred_col = 'Predicted SEP Peak Intensity (Onset Peak)'
            release_obs_col  = 'Observed SEP Peak Intensity Max (Max Flux)'

        # LOAD AND CONCATENATE ALL MATCHING RELEASE CSV FILES
        release_frames = []
        if os.path.isdir(RELEASE_DIR):
            for fname in os.listdir(RELEASE_DIR):
                if fname.startswith(release_file_prefix) and fname.endswith('_mm_Max.csv'):
                    try:
                        frame = pd.read_csv(os.path.join(RELEASE_DIR, fname))
                        release_frames.append(frame)
                    except Exception:
                        pass
        release_df = pd.concat(release_frames, ignore_index=True) if release_frames else pd.DataFrame()

        # FILTER df TO NON-REleASE MODELS ONLY FOR STANDARD COLUMN PLOTTING
        is_release = df['Model'].str.contains('REleASE', case=False, na=False)
        non_release_df = df[~is_release]

        all_categories = sorted(df['Model Category'].unique())
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
                i = all_categories.index(cat) if cat in all_categories else 0
                color = config.color.color_cycle[i % len(config.color.color_cycle)]
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
        plt.savefig(save, dpi=config.image.dpi, bbox_inches='tight')
        plt.close()

    return True, build_html.build_image(save, write_as_base64=convert_image_to_base64)


def build_peak_flux_legend(df, save, convert_image_to_base64=False):
    """Build a standalone legend image for the peak flux plots,
    one entry per Model Category present in df."""
    categories = sorted(df['Model Category'].unique())
    if not categories:
        return ''

    handles = [
        matplotlib.patches.Patch(
            color=config.color.color_cycle[i % len(config.color.color_cycle)],
            label=cat)
        for i, cat in enumerate(categories)
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
        plt.savefig(save, dpi=config.image.dpi, bbox_inches='tight')
        plt.close()

    return build_html.build_image(save, write_as_base64=convert_image_to_base64)
