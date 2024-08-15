from ..utils import build_html
from ..utils import tabulate_contingency_metrics
from ..utils import plot_peak_flux
from ..utils import plot_probability
from ..utils import config

import os

def build_model_section(df, weekly_df, week_start, week_end):
    text = build_html.build_section_title('Model Performance')
    text += tabulate_contingency_metrics.build_all_clear_contingency_table(df, week_start, week_end)
    text += tabulate_contingency_metrics.build_false_alarm_table(weekly_df)
    text += plot_peak_flux.build_peak_flux_plot(weekly_df, os.path.join(config.path.email_image, 'predicted-peak-flux-vs-observed-peak-flux.jpg'))
    text += plot_probability.build_probability_plots(weekly_df, os.path.join(config.path.email_image, 'probability-histogram.jpg'))
    return text

