from ..utils import build_html
from ..utils import config
from ..utils import filter_objects

import matplotlib
import matplotlib.pyplot as plt

plt.rcParams['font.family'] = config.plot.font
plt.rcParams['font.size'] = config.plot.fontsize

def plot_predicted_peak_flux_vs_observed_peak_flux(title, df, save, min_peak, max_peak):
    plt.figure(figsize=(config.image.peak_flux_width, config.image.peak_flux_height))
    color_counter = 0
    plot_exists = False
    for name, group in df.groupby('Model Category'):
        if not filter_objects.is_column_empty(group, 'Predicted SEP Peak Intensity (Onset Peak)'):
            plot_exists = True
            plt.scatter(group['Observed SEP Peak Intensity (Onset Peak)'], group['Predicted SEP Peak Intensity (Onset Peak)'], label=name, s=config.plot.marker_size, color=config.color.color_cycle[color_counter])
            color_counter += 1
    if plot_exists:  
        plt.plot([min_peak, max_peak], [min_peak, max_peak], color='black', linestyle='--')
        plt.grid()
        plt.title(title)
        plt.xlabel('Observed Peak Flux [pfu]')
        plt.ylabel('Predicted Peak Flux [pfu]')
        plt.xscale('log')
        plt.yscale('log')
        plt.xlim([min_peak, max_peak])
        plt.ylim([min_peak, max_peak])
        plt.legend(loc='upper left', framealpha=config.plot.opacity, fontsize='small')
        plt.tight_layout()
        plt.savefig(save, dpi=config.image.dpi, bbox_inches=0)
        plt.close()

def build_peak_flux_plot(title, df, savefile, min_peak, max_peak, convert_image_to_base64=False):
    plot_predicted_peak_flux_vs_observed_peak_flux(title, df, savefile, min_peak, max_peak)
    text = build_html.build_image(savefile, write_as_base64=convert_image_to_base64)
    return text
