import pandas as pd

class Subscriber:
    def __init__(self):
        self.email = ''
        self.name = ''
        self.models = []
   

    def define_email(self, email):
        self.email = email        
 
    def define_name(self, first, last, middle=''):
        self.name = first + ' '
        if not pd.isna(middle) and type(middle) == str:
            self.name += middle + ' '
        self.name += last

    def add_models(self, model_string):
        self.models = model_string.split(',')    
    
def load_subscribers(filename):
    """
    Reads the subscriber list and applies subscriber-specific options.
    
    Parameters
    ----------
    filename : string
        Path to file that contains list of MailSPHINX recipients with subscriber options; SSV-CSV format.
    """
    df = pd.read_csv(filename, delimiter=';')
    subscribers = []
    for i in range(0, len(df)):
        subscriber = Subscriber()
        subscriber.define_email(df['Subscriber'].iloc[i])
        subscriber.define_name(df['First_Name'].iloc[i], df['Last_Name'].iloc[i], middle=df['Middle_Name'].iloc[i])
        print(df['Model'].iloc[i])
        subscriber.add_models(df['Model'].iloc[i])
        subscribers.append(subscriber)
    return subscribers





