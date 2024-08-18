from ..utils import filter_objects
from ..utils import build_html
from ..utils import config

import os
import glob
import matplotlib.pyplot as plt
import matplotlib
plt.rcParams['font.family'] = config.plot.font
plt.rcParams['font.size'] = config.plot.fontsize
plt.rcParams['axes.prop_cycle'] = plt.cycler(color=config.color.color_cycle)


def plot_probability_histograms(df, save):
    counter = 0
    save_without_extension, extension = os.path.splitext(save)
    last_name, last_group = list(reversed(list(iter(df.groupby('Model Category')))))[0]
    for name, group in df.groupby('Model Category'):
        data_list = []
        label_list = []
        if not filter_objects.is_column_empty(group, 'Predicted SEP Probability'):
            plt.figure(figsize=(config.image.width, config.image.height))
            for subname, subgroup in group.groupby('Model Flavor'):
                label_list.append(subname)
                data_list.append(subgroup['Predicted SEP Probability'])
            if data_list != []:
                plt.hist(data_list, bins=20, stacked=True, label=label_list)
                plt.title(name + ' Predicted SEP Probability Distribution')
                plt.ylabel('Number of Forecasts')
                plt.grid(True)
                plt.xlim([0, 1])
                if (name == last_name) and group.equals(last_group):
                    plt.xlabel('Predicted SEP Probability')
                plt.legend(loc='upper right')
                plt.tight_layout()
                plt.savefig(save.replace(extension, '-' + str(counter) + extension), dpi=config.image.dpi, bbox_inches=0)
                counter += 1

def plot_probability_histogram(df, save, main_model=''):
    plt.figure(figsize=(config.image.width, config.image.height))
    for subname, subgroup in df.groupby('Model Flavor'):
        plt.hist(subgroup['Predicted SEP Probability'], bins=20, stacked=True, label=subname)
    plt.title(main_model + ' Predicted SEP Probability Distribution')
    plt.ylabel('Number of Forecasts')
    plt.grid(True)
    plt.xlim([0, 1])
    plt.xlabel('Predicted SEP Probability')
    plt.legend(loc='upper right')
    plt.tight_layout()
    plt.savefig(save, dpi=config.image.dpi, bbox_inches=0)
    
def build_probability_plot(model, df, savefile, week_start, week_end, events, need_legend=False):
    #plot_probability_histogram(df, savefile)
    plot_probability_time_series_group(model, df, savefile, week_start, week_end, events, need_legend=need_legend)
    text = build_html.build_image(savefile, image_width_percentage=config.html.probability_width_percentage)
    return text

def plot_probability_time_series_group(name, group, save, week_start, week_end, events, colors=config.color.color_cycle, bins=20, need_legend=False):

    fig, ax = plt.subplots(1, 2, figsize=(config.image.width, config.image.height), gridspec_kw={'width_ratios' : [3, 1], 'wspace' : 0}, sharey=True)
    color_counter = 0
    for subname, subgroup in group.groupby('Model Flavor'):
        if not filter_objects.is_column_empty(subgroup, 'Predicted SEP Probability'):
            plot_probability_time_series_subgroup(ax, subname, subgroup, colors[color_counter], bins)
            color_counter += 1

    ax[0].set_title(name + ' SEP Probability')
    ax[0].set_xlabel('UTC')
    ax[0].set_xlim([week_start, week_end])
    ax[0].set_xticklabels(ax[0].get_xticks(), rotation=45)
    ax[0].set_ylim([0.0, 1.0])
    ax[0].set_ylabel('Predicted SEP Probability')
    ax[0].grid(True)
    ax[0].set_aspect(aspect='auto')
    ax[0].xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y-%m-%d')) 
    for index, event in events.iterrows():
        ax[0].axvspan(event['Observed SEP Threshold Crossing Time'], event['Observed SEP End Time'], color=config.color.associations[event['Energy']], alpha=config.plot.opacity)


    ax[1].set_xlabel('Forecasts')
    ax[1].grid(True)
    ax[1].set_aspect(aspect='auto')
    ax[1].set_ylim(ax[0].get_ylim())
    
    plt.subplots_adjust(wspace=0)
    for i in range(0, len(ax)):
        for spine in ax[i].spines.values():
            spine.set_linewidth(4)
    
    if need_legend:
        ax[1].legend(loc='upper right')
    plt.tight_layout(pad=0.5)
    plt.subplots_adjust(left=config.html.left_padding_fraction / config.html.probability_width_percentage * 100)
    plt.savefig(save, dpi=config.image.dpi, bbox_inches=0)
    plt.close()
    
def plot_probability_time_series_subgroup(ax, subname, subgroup, color, bins):
    ax[0].scatter(subgroup['Prediction Window Start'], subgroup['Predicted SEP Probability'], color=color, label=subname, facecolor='none', s=config.plot.marker_size)  
    ax[1].hist(subgroup['Predicted SEP Probability'], bins=bins, orientation='horizontal', color=color, alpha=0.25, label=subname)





    
    
    



