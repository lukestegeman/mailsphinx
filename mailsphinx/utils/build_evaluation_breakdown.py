"""Build the Evaluation Breakdown section for the MailSPHINX email.

This section appears at the very end of the email and shows counts of
unevaluated forecasts broken down by All Clear Match Status reason,
per (energy channel, threshold) pair.

The breakdown data is computed alongside the All Clear Contingency
Tables in tabulate_contingency_metrics.py and passed in directly,
avoiding any recomputation.
"""

from ..utils import build_html
from ..utils import config
from ..utils import manipulate_keys


# ABBREVIATED LABELS FOR NOT-EVALUATED MATCH STATUSES.
# KEPT HERE AS THE SINGLE SOURCE OF TRUTH — IMPORTED BY
# tabulate_contingency_metrics.py TO AVOID DUPLICATION.
NE_ABBREVIATIONS = {
    'Ongoing SEP Event':                                                      'OSE',
    'No SEP Event':                                                           'NSE',
    'Trigger not associated with observed SEP':                               'TNS',
    'SEP Event':                                                              'SE',
    'No SEP Event (SubEvent)':                                                'NSE-S',
    'Trigger/Input after Observed Phenomenon':                                'TIA',
    'Trigger associated with observed SEP but SEP not in prediction window':  'TSPW',
}

# OUTCOME ASSOCIATED WITH EACH NOT-EVALUATED MATCH STATUS ABBREVIATION.
NE_OUTCOMES = {
    'OSE':   'Forecast not evaluated',
    'NSE':   'No observed SEP event/Clear',
    'TNS':   'No observed SEP event/Clear',
    'SE':    'Observed SEP event/Not Clear',
    'NSE-S': 'Observed SEP event below threshold/Clear',
    'TIA':   'Forecast not evaluated',
    'TSPW':  'Forecast not evaluated',
}


def build_ne_legend():
    """Build a legend table mapping abbreviations to full match status
    names and their associated forecast outcome."""
    headers = ['Abbreviation', 'Forecast-Observation Match Status', 'Outcome']
    table_data = [
        [abbrev, full, NE_OUTCOMES[abbrev]]
        for full, abbrev in NE_ABBREVIATIONS.items()
    ]
    return build_html.build_table(headers, table_data)


def build_evaluation_breakdown(breakdown_sections):
    """Build the Evaluation Breakdown section.

    Parameters
    ----------
    breakdown_sections : list of (label, breakdown_table_data)
        Each entry is a channel label string and a list of table rows,
        as produced by tabulate_contingency_metrics.build_contingency_table_data.

    Returns
    -------
    text : str
        HTML for the Evaluation Breakdown section.
    """
    ne_abbrev_list = list(NE_ABBREVIATIONS.values())
    breakdown_headers = ['Model Category', 'Model Variant'] + ne_abbrev_list

    text = build_html.build_section_title('Evaluation Breakdown')
    text += build_html.build_regular_text(
        "Counts of forecasts by match status reason for traceability. "
        "Values are in the form X (+Y) as above.")
    text += build_ne_legend()

    for label, breakdown_table_data in breakdown_sections:
        if breakdown_table_data:
            text += build_html.build_paragraph_title(label, sublevel=1)
            text += build_html.build_table(breakdown_headers, breakdown_table_data)

    text += build_html.build_divider()
    return text
