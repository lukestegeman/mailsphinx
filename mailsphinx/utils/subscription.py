from ..utils import config

import pandas as pd

class Subscriber:
    def __init__(self):
        self.email = ''

    def define_email(self, email):
        self.email = email        
 
def load_subscribers():
    """
    Reads the subscriber list and applies subscriber-specific options. 
    """
    #df = get_googlesheet_as_dataframe()
    df = pd.read_csv(config.path.subscriber_data)
    subscribers = []
    for index, row in df.iterrows():
        subscriber = Subscriber()
        subscriber.define_email(row['email'])
        subscribers.append(subscriber)
    return subscribers


