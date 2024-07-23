import pandas as pd
import gspread
from datetime import date
import re
from google.oauth2.service_account import Credentials
from datetime import date, timedelta

# Update all status cells with the labels "DUE" or 'UPCOMING"
def prelim_activeTaskModify(client, ss_id):
    sheet = client.open_by_key(ss_id).get_worksheet(1) #Get's second sheet
    matches_due = sheet.findall("DUE")
    for cell in matches_due:
        cell.value = "OVERDUE"
    matches_upc = sheet.findall("UPCOMING")
    for cell in matches_upc:
        cell.value = "DUE"
    sheet.update_cells(matches_due + matches_upc)

#Adds new UPCOMING tasks
def post_activeTaskModify(client, ss_id, startDate = None, endDate = None):
    #Get both sheets
    full_cleaning_sheet = client.open_by_key(ss_id).get_worksheet(0) #Get's second sheet
    active_sheet = client.open_by_key(ss_id).get_worksheet(1) #Get's first sheet

    #If no start date OR end date is passed, autogenerate them
    if startDate == None or endDate == None:
        startDate = date.today() + timedelta(days=7)
        endDate = date.today() + timedelta(days=14)
    print("Start Date: " + str(startDate))
    print("End_Date: " + str(endDate))
    endDate_values = str(endDate).split("-")
    startDate_values = str(startDate).split("-")

    #Construct regex and use to find upcoming dates within the Full_Cleaning_Schedule
    subregex = '('
    dateRange = endDate - startDate
    for i in range(dateRange.days + 1):
        d = (startDate +timedelta(days=i)).day
        if d < 10:  # Converts single digit days into 2-digits
            subregex += ('0'+str(d) + "|")
        else:
            subregex += (str(d) + "|")
    subregex = subregex[:-1] + ')'
    regex = r"(" + startDate_values[1] + "|" + endDate_values[1] + ")\\-" + subregex + "\\-(" + startDate_values[0] + "|" + endDate_values[0] + ")"
    #print("Regex:", regex)
    criteria_regex = re.compile(regex)

    #Get Area & Tasks for rows with upcoming dates
    list_of_rows = full_cleaning_sheet.get_all_values()
    area_col = list_of_rows[0].index("Area/Descriptor")
    task_col =  list_of_rows[0].index("Task")
    
    #Collect the upcoming tasks from rows that fall within the range
    upcomingCleaning = [] #List of Lists
    for row in list_of_rows:
        for cell in row:
            match = re.search(criteria_regex, cell)
            if match:
                upcomingCleaning.append([row[area_col], row[task_col], "UPCOMING"])    
                index_of_match = row.index(cell)
                print(f"\t-Regex Pattern found in '{cell}' at index {index_of_match} in row {row}")
    #print(upcomingCleaning)

    #Commit updates
    active_sheet.append_rows(upcomingCleaning, value_input_option="USER_ENTERED")

# Test functions 
'''
from auth import SERVICE_KEY_JSON_FILE, SPREADSHEET_ID

#SPREADSHEET_ID = os.environ['SPREADSHEET_ID']
#SERVICE_KEY_JSON_FILE = os.environ['SERVICE_KEY_JSON_FILE']

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
creds = Credentials.from_service_account_info(SERVICE_KEY_JSON_FILE, scopes=SCOPES)
client = gspread.authorize(creds)
prelim_activeTaskModify(client, SPREADSHEET_ID)
post_activeTaskModify(client, SPREADSHEET_ID)
'''