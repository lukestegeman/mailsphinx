from ..utils import config

import matplotlib
import matplotlib.lines
import matplotlib.pyplot as plt
import os

def build_legend():
    fig, ax = plt.subplots(figsize=(config.image.width_legend, config.image.height_legend))
    handles = []
    handles += build_legend_space_weather()
    handles += build_legend_contingency()
    handles += build_legend_event()
    ax.legend(handles=handles, loc='center', ncol=2, borderpad=0, borderaxespad=0, frameon=False)
    ax.axis('off')
    plt.tight_layout(pad=0.1)
    plt.savefig(os.path.join(config.path.email_image, 'legend.jpg'), bbox_inches='tight', pad_inches=0.0, transparent=True, dpi=config.image.dpi)

def build_legend_peak_flux_separate():
    fig, ax = plt.subplots(figsize=(config.image.width_legend, config.image.height_legend))
    handles = []
    handles += build_legend_peak_flux()
    ax.legend(handles=handles, loc='center', ncol=1, borderpad=0, borderaxespad=0, frameon=False)
    ax.axis('off')
    plt.tight_layout(pad=0.1)
    plt.savefig(os.path.join(config.path.email_image, 'legend-peak-flux.jpg'), bbox_inches='tight', pad_inches=0.0, transparent=True, dpi=config.image.dpi)

def build_legend_peak_flux():
    legend_labels = ['Onset Peak',
                     'Max Flux',
                     'Max Flux in Prediction Window',
                    ]
    legend_markers = []
    legend_colors = []
    for label in legend_labels:
        legend_markers.append(config.shape.associations[label])
        legend_colors.append('black')
    handles = []
    for marker, color, label in zip(legend_markers, legend_colors, legend_labels):
        handles.append(matplotlib.lines.Line2D([0], [0], marker=marker, color=config.color.legend_background, markerfacecolor='none', markeredgecolor=color, markersize=config.plot.marker_size // 10, label=label))
    return handles 

def build_legend_contingency():
    legend_labels =  ['Hits',
                      'Misses',
                      'False Alarms',
                      'Correct Negatives',
                      #'Eruption Out of Range',
                      'Trigger/Input after Observed Phenomenon',
                      'No Matching Threshold',
                      'Ongoing SEP Event',
                      #'No Prediction Provided',
                      #'Unmatched',
                     ]               
    legend_markers = []
    legend_colors = []
    for label in legend_labels:
        legend_markers.append(config.shape.associations[label])
        legend_colors.append(config.color.associations[label])

    handles = []
    for marker, color, label in zip(legend_markers, legend_colors, legend_labels):
        handles.append(matplotlib.lines.Line2D([0], [0], marker=marker, color=config.color.legend_background, markerfacecolor='none', markeredgecolor=color, markersize=config.plot.marker_size // 10, label=label))
    return handles

def build_legend_space_weather():
    legend_labels =  [
                     'Long X-Ray Flux',
                     'Short X-Ray Flux',
                     '38-53 keV Electron Flux',
                     '175-315 keV Electron Flux',
                     '$\geq$ 5 MeV Proton Flux',
                     '$\geq$ 10 MeV Proton Flux',
                     '$\geq$ 30 MeV Proton Flux',
                     '$\geq$ 50 MeV Proton Flux',
                     '$\geq$ 60 MeV Proton Flux',
                     '$\geq$ 100 MeV Proton Flux',
                     '$\geq$ 500 MeV Proton Flux',
                      ]
    handles = [] 
    for label in legend_labels:
        if 'Proton' in label:
            key = '>=' + label.lstrip('$\geq$ ')
        elif ('X-Ray' in label) or ('Electron' in label):
            key = label
        handles.append(matplotlib.lines.Line2D([0], [0], color=config.color.associations[key], lw=2, label=label))
    return handles

def build_legend_event():
    legend_labels = [
                    '$\geq$ 10 MeV, $\geq$ 10 pfu Event',
                    '$\geq$ 30 MeV, $\geq$ 1 pfu Event',
                    '$\geq$ 50 MeV, $\geq$ 1 pfu Event',
                    '$\geq$ 100 MeV, $\geq$ 1 pfu Event'
                    ]
    handles = [] 
    for label in legend_labels:
        key = label.replace('$\geq$ ', '>=')
        handles.append(matplotlib.patches.Patch(color=config.color.associations[key], label=label))
    return handles
