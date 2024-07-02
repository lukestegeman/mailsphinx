from ..utils import scoreboard_call

def build_text(subscriber):
    """
    Writes the text that makes up the email body.

    Parameters
    ----------
    subscriber : Subscriber() object

    Returns
    -------
    text : string
    """
    text = "Hi " + subscriber.name + ',\n'
    text += "Take a look at this week's SPHINX report(s)! [test; do not reply]\n\n"
    text += "Models you're subscribed to:\n"
    for model in subscriber.models:
        text += model + '\n'

    text += scoreboard_call.build_scoreboard_links_text(subscriber)

    return text
