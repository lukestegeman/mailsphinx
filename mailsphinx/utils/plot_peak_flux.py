from ..utils import filter_objects
from ..utils import build_html
from ..utils import config

import matplotlib.pyplot as plt
import matplotlib
plt.rcParams['font.family'] = config.plot.font
plt.rcParams['font.size'] = config.plot.fontsize

def plot_predicted_peak_flux_vs_observed_peak_flux(df, save):
    plt.figure(figsize=(10,6))
    for name, group in df.groupby('Model Category'):
        if not filter_objects.is_column_empty(group, 'Predicted SEP Peak Intensity (Onset Peak)'):
            plt.scatter(group['Observed SEP Peak Intensity (Onset Peak)'], group['Predicted SEP Peak Intensity (Onset Peak)'], label=name, s=20)
    plt.grid()
    plt.xlabel('Observed Peak Flux [pfu]')
    plt.ylabel('Predicted Peak Flux [pfu]')
    plt.xscale('log')
    plt.yscale('log')
    plt.legend(loc='upper left', bbox_to_anchor=(1.05, 1), fontsize='small')
    plt.tight_layout()
    plt.savefig(save, dpi=config.image.dpi, bbox_inches=0)

def build_peak_flux_plot(df, savefile):
    text = build_html.build_paragraph_title('Predicted Peak Flux vs. Observed Peak Flux')
    plot_predicted_peak_flux_vs_observed_peak_flux(df, savefile)
    text += build_html.build_image(savefile)
    return text
