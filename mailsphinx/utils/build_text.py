from ..utils import scoreboard_call
from ..utils import config

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
    text = "Hi " + subscriber.name + ',<br>'
    text += "Take a look at this week's SPHINX report(s)! [test; do not reply]<br><br>"
    text += "Models you're subscribed to:<br>"
    for model in subscriber.models:
        text += model + '<br>'

    text += scoreboard_call.build_scoreboard_links_text(subscriber)
    
    unsubscribe_link = config.google_script_url + '?email=' + subscriber.email
    text += '<br><br><br>'
    text += '<a href="' + unsubscribe_link + '">Unsubscribe</a><br><br>'
    text += 'If the link above fails, copy & paste this URL into your browser: <p>' + unsubscribe_link + '</p>'

    return text
