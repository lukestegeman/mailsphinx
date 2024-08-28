from ..utils import build_html
from ..utils import config
from ..utils import filter_objects

import os
import glob
import math
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import warnings

plt.rcParams['font.family'] = config.plot.font
plt.rcParams['font.size'] = config.plot.fontsize
plt.rcParams['axes.prop_cycle'] = plt.cycler(color=config.color.color_cycle)

def build_probability_plot(model, df, savefile, week_start, week_end, events, need_legend=False, convert_image_to_base64=False):
    plot_probability_time_series_group(model, df, savefile, week_start, week_end, events, need_legend=need_legend)
    text = build_html.build_image(savefile, image_width_percentage=config.html.probability_width_percentage, write_as_base64=convert_image_to_base64)
    return text

def plot_probability_time_series_group(name, group, save, week_start, week_end, events, colors=config.color.color_cycle, need_legend=False):

    if need_legend:
        height_ratios = [1, 2]
    else:
        height_ratios = [1, 2]


    fig, ax = plt.subplots(2, 2, figsize=(config.image.width, config.image.height), gridspec_kw={'width_ratios' : [3, 1], 'wspace' : 0, 'height_ratios' : height_ratios, 'hspace' : 0}, sharey=True)
    color_counter = 0
    max_probability = 0
    for subname, subgroup in group.groupby('Model Flavor'):
        if not filter_objects.is_column_empty(subgroup, 'Predicted SEP Probability'):
            if subgroup['Predicted SEP Probability'].max() > max_probability:
                max_probability = subgroup['Predicted SEP Probability'].max()
            plot_probability_time_series_subgroup(ax, subname, subgroup, colors[color_counter])
            color_counter += 1
    ax[1, 0].set_title(name + ' SEP Probability')
    xticks = pd.date_range(week_start, week_end)
    ax[1, 0].set_xticks(xticks)
    counter = 0
    labels = []
    for date in ax[1, 0].get_xticklabels():
        if counter == 0 or counter == len(ax[1, 0].get_xticklabels()) - 1:
            label = date
        else:
            label = ''
        labels.append(label)
        counter += 1
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', UserWarning)
        ax[1, 0].set_xticklabels(labels)
    fig.autofmt_xdate(rotation=0, ha='center')
    ax[1, 0].set_xlim([week_start, week_end])
    ax[1, 0].set_ylim(bottom=0.0)
    ax[1, 0].set_ylabel('Predicted SEP Probability')
    for index, event in events.iterrows():
        ax[1, 0].axvspan(event['Observed SEP Threshold Crossing Time'], event['Observed SEP End Time'], color=config.color.associations[event['Energy']], alpha=config.plot.opacity)
    ax[1, 0].grid(True)
    ax[1, 0].set_aspect(aspect='auto')
    ax[1, 1].set_xlabel('Forecasts')
    labels = ax[1, 1].get_xticklabels()
    labels[0] = ''
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', UserWarning)
        ax[1, 1].set_xticklabels(labels)
    ax[1, 1].grid(True)
    ax[1, 1].set_aspect(aspect='auto')
    ax[1, 1].set_ylim([0.0, round(math.ceil(max_probability * 100) / 100 + 0.01, 2)])
    
    plt.subplots_adjust(wspace=0)
    for i in range(0, len(ax)):
        for spine in ax[i, 1].spines.values():
            spine.set_linewidth(1)
            #spine.set_linewidth(4)

    ax[0, 0].axis('off')
    ax[0, 1].axis('off')
    if need_legend:
        plot_bbox = ax[1, 1].get_position()
        handles, labels = ax[1, 1].get_legend_handles_labels()
        legend = ax[0, 1].legend(handles=handles, labels=labels, loc='center', bbox_to_anchor=(0.5, 0.5), bbox_transform=ax[0, 1].transAxes, fontsize=12)
        legend_box = legend.get_frame()
        legend_box.set_width(plot_bbox.width * config.image.dpi)
    plt.tight_layout(pad=0.5)
    #fig.patch.set_facecolor('blue')
    #plt.subplots_adjust(left=config.html.left_padding_fraction / config.html.probability_width_percentage * 100)
    plt.subplots_adjust(left=config.html.left_padding_fraction * 0.875)
    plt.savefig(save, dpi=config.image.dpi, bbox_inches=0)
    plt.close()
    
def plot_probability_time_series_subgroup(ax, subname, subgroup, color):
    ax[1, 0].scatter(subgroup['Prediction Window Start'], subgroup['Predicted SEP Probability'], color=color, label=subname, facecolor='none', s=config.plot.marker_size)  
    ax[1, 1].hist(subgroup['Predicted SEP Probability'], bins=100, range=(0, 1), orientation='horizontal', color=color, stacked=True, label=subname)





    
    
    



