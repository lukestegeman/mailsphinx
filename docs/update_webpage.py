import openpyxl
import gspread
from oauth2client.service_account import ServiceAccountCredentials as sac

def get_googlesheet_rows():
    """
    Extracts rows from Google Sheet that contains subscriber preferences.
    """
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = sac.from_json_keyfile_name('../security/mailsphinx-8010bb19634b.json', scope)
    client = gspread.authorize(creds)
    sheet = client.open('mailsphinx-subscriber-data').sheet1
    rows = sheet.get_all_values()
    return rows

def update_googlesheet(data):
    """
    Updates Google Sheet that contains subscriber preferences.
    
    Parameters
    ----------
    data -- list[list[string]]
            List of list of strings containing rows of data to be written to Google Sheet.
    """

    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = sac.from_json_keyfile_name('../security/mailsphinx-8010bb19634b.json', scope)
    client = gspread.authorize(creds)
    sheet = client.open('mailsphinx-subscriber-data').sheet1
    sheet.clear()
    for row in data:
        sheet.append_row(row)

if __name__ == '__main__':
    
    # READ MODEL LIST FILE
    filename = 'model-list.txt'
    a = open(filename, 'r')
    read = a.readlines()
    a.close()
    
    category_marker = ':~:'

    model_dict = {}
    
    for i in range(0, len(read)):
        line = read[i].rstrip('\n')
        if category_marker in line:
            category = line.split(category_marker)[0]
            model_dict[category] = []
        else:
            model_dict[category].append(line)
   
    # CREATE NEW CHECKBOX STRING
    checkbox_string = ''
    model_list = []
    for category, models in model_dict.items():
        checkbox_string += '                <br><br><h2>' + category + ' Models</h2>\n'
        for model in models:
            checkbox_string += '            <label>\n'
            checkbox_string += '                <input name="' + model + '" type="checkbox" id="' + model + '" value="1">\n'
            checkbox_string += '                <span>' + model + '</span>\n'
            checkbox_string += '            </label>\n'
            model_list.append(model)

    # REPLACE ${checkboxes}$ IN index_template.html
    a = open('index_template.html', 'r')
    read = a.read()
    a.close()

    write_string = read.replace('${checkboxes}$', checkbox_string)
    a = open('index.html', 'w')
    a.write(write_string)
    a.close()

    # READ FROM GOOGLE SHEET
    rows = get_googlesheet_rows()    
    subscriber_preferences_old = {}
    subscriber_preferences_old_list = []
    counter = 0
    label = []
    for row in rows:
        if counter == 0:
            for index in range(0, len(row)):
                label.append(row[index])
        else:
            for index in range(0, len(row)):   
                subscriber_preferences_old[label[index]] = row[index]
            subscriber_preferences_old_list.append(subscriber_preferences_old)
        counter += 1

    # WRITE TO GOOGLE SHEET
    label_list = ['timestamp', 'email', 'name'] + model_list
    spreadsheet_data = [label_list]
    for i in range(0, len(subscriber_preferences_old_list)):
        row = []
        for j in range(0, len(label_list)):
            if not (label_list[j] in subscriber_preferences_old_list[i].keys()):
                subscriber_preferences_old_list[i][label_list[j]] = ''
            new_value = subscriber_preferences_old_list[i][label_list[j]]
            row.append(new_value)
        spreadsheet_data.append(row)
    update_googlesheet(spreadsheet_data)
    print('mailsphinx-subscriber-data updated (https://docs.google.com/spreadsheets/d/1PJlkhI0aimpJH2o7KaN62-Lx0Hp_e-DQoPqi8KjiEC4/edit?gid=0#gid=0)')

