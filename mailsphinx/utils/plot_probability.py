from ..utils import filter_objects
from ..utils import build_html
from ..utils import config

import os
import glob
import matplotlib.pyplot as plt
import matplotlib
plt.rcParams['font.family'] = config.plot.font
plt.rcParams['font.size'] = config.plot.fontsize


def plot_probability_histograms(df, save):
    counter = 0
    save_without_extension, extension = os.path.splitext(save)
    last_name, last_group = list(reversed(list(iter(df.groupby('Model Category')))))[0]
    for name, group in df.groupby('Model Category'):
        data_list = []
        label_list = []
        if not filter_objects.is_column_empty(group, 'Predicted SEP Probability'):
            plt.figure(figsize=(10, 5))
            plt.rcParams['axes.prop_cycle'] = plt.cycler(color=config.color.color_cycle)
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

def build_probability_plots(df, savefile):
    text = build_html.build_paragraph_title('Probability Histograms')
    plot_probability_histograms(df, savefile)
    savefile_without_extension, extension = os.path.splitext(savefile)
    savefiles = glob.glob(savefile_without_extension + '-*' + extension)
    for savefile in savefiles:
        print(savefile)
        text += build_html.build_image(savefile)
    return text

