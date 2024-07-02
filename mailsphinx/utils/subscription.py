import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def get_googlesheet_as_dataframe():
    """
    Builds a pandas DataFrame from subscriber data Google Sheet.    

    Parameters
    ----------

    Returns
    -------
    df : Pandas DataFrame object with mailsphinx-subscriber-data Google Sheet
    """

    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name('../security/mailsphinx-8010bb19634b.json', scope)
    client = gspread.authorize(creds)
    sheet = client.open('mailsphinx-subscriber-data')
    worksheet = sheet.get_worksheet(0)
    records = worksheet.get_all_records()
    df = pd.DataFrame.from_records(records)
    parsed_df = reformat_subscriber_df(df)
    return parsed_df

def reformat_subscriber_df(df):
    """
    Reformats DataFrame containing subscriber information for further processing.

    Parameters
    ----------
    df : Pandas DataFrame containing subscriber information. Pulled from Google Sheets.
    """
    df = df.rename(columns={'email' : 'Subscriber',
                            'name' : 'Name'})
    df = df.replace('', 0)
    df = df.replace('1', 1)
    df_models = df.drop(columns=['Subscriber', 'Name', 'timestamp'])
    model_list = []
    for i in range(0, len(df_models)):
        model_string = ''
        for j in range(0, len(df_models.iloc[i])):
            model_string += df_models.iloc[i].iloc[j] * df_models.columns[j] + ','
        model_string = model_string.rstrip(',')
        model_list.append(model_string)
    df['Model'] = model_list
    return df

class Subscriber:
    def __init__(self):
        self.email = ''
        self.name = ''
        self.models = []

    def define_email(self, email):
        self.email = email        
 
    def define_name(self, name):
        self.name = name

    def add_models(self, model_string):
        self.models = model_string.split(',')

def load_subscribers():
    """
    Reads the subscriber list and applies subscriber-specific options. 
    """
    df = get_googlesheet_as_dataframe()
    subscribers = []
    for i in range(0, len(df)):
        subscriber = Subscriber()
        subscriber.define_email(df['Subscriber'].iloc[i])
        subscriber.define_name(df['Name'].iloc[i])
        subscriber.add_models(df['Model'].iloc[i])
        subscribers.append(subscriber)
    return subscribers





