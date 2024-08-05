import gspread, time, os, json
import pandas as pd
from datetime import date, datetime
from ss_manip import readCSVFiles
from jolt_scraper_v4 import downloadCSVs
from activeTask_manip import prelim_activeTaskModify, post_activeTaskModify
from google.oauth2.service_account import Credentials
from slack_blocks import headerBlock, dividerBlock, markdownBlock, runBlocks 


#Function used for properly formatting a readable task name for messaging purposes
def formatTaskName(task):
    if " (Left)" in task:
        task = task.replace(" (Left)", "").strip()
        task = "Left Side of " + task
    elif " (Right)" in task:
        task = task.replace(" (Right)", "").strip()
        task = "Right Side of " + task
    return task

#Checks a Status' output string to see if a task exists there
def checkStatusString(string, stringName):
    if len(string) > 0:
        return [headerBlock(stringName), markdownBlock(string)]
    return []

# Set up credentials and other Variables
#from auth import SERVICE_KEY_JSON_FILE, SPREADSHEET_ID, MASTER_SPREADSHEET_ID
SPREADSHEET_ID = os.environ['SPREADSHEET_ID']
MASTER_SPREADSHEET_ID = os.environ['MASTER_SPREADSHEET_ID']
SERVICE_KEY_JSON_FILE = json.loads(os.environ["SERVICE_KEY_JSON_FILE"])

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
creds = Credentials.from_service_account_info(SERVICE_KEY_JSON_FILE, scopes=SCOPES)
client = gspread.authorize(creds)

listNames = ["BOH Cleaning List"]

#Update Status Codes of tasks in Active Task Spreadsheet
prelim_activeTaskModify(client, SPREADSHEET_ID)
time.sleep(5)

#Try Download Completed Jolt List Data
path = downloadCSVs(listNames)

#Gathers a dictionary of cleaned tasks and updates cleaning dates
result = readCSVFiles(path, client, SPREADSHEET_ID, MASTER_SPREADSHEET_ID)       #Prints a dictionary of the important data types
time.sleep(5)

#Update the Active Task Spreadsheet with upcoming tasks and removes completed tasks
post_activeTaskModify(client, SPREADSHEET_ID, result, date(2024,7,31), date(2024,8,20))

# Slack Messaging and Data processing

#Setup some basic string variables
overdue = ""
due = ""
upcoming = ""
errored = ""


#Gather Spreadsheet Data
masterData = client.open_by_key(SPREADSHEET_ID).get_worksheet(0).get_all_values()
activeData = client.open_by_key(SPREADSHEET_ID).get_worksheet(1).get_all_values()

#Turn data into DataFrames
masterDF = pd.DataFrame(masterData[1:], columns=masterData[0])
activeDF = pd.DataFrame(activeData[1:], columns=activeData[0])

#Merge Data Frames
mergedDF = pd.merge(activeDF, masterDF, on=['Area/Descriptor', 'Task'], how='left')

#Reorder to gather relevant data
ssData = mergedDF[['Area/Descriptor', 'Task', 'Status', 'Next Cleaning Date']]

#Cycle through each row in DataFrame
for index, row in ssData.iterrows():
    #Format date properly
    date = datetime.strptime(row['Next Cleaning Date'], '%m-%d-%Y')
    date = date.strftime('%m/%d/%y').replace('/0', '/').replace(' 0', ' ')
    
    #Basic task name format
    taskName = row['Area/Descriptor'] + " " + row['Task']
    
    #Format Task Name based upon specific tasks
    taskName = formatTaskName(taskName)

    output = f"• *{taskName}* (Due: {date})\n"
    status = str(row['Status'])
    if status.lower() == 'overdue':
        overdue = overdue + output
    elif status.lower() == 'due':
        due = due + output
    elif status.lower() == "upcoming":
        upcoming = upcoming + output
    else:
        errored = errored + output

#List of blocks to send to Slack
blocks = []

#List of status names and their contents
statuses = [
    ('OVERDUE', overdue),
    ('DUE', due),
    ('UPCOMING', upcoming),
    ('INVALID STATUS', errored)
]

#Iterate through above list and append proper data to blocks
for i, (status_name, content) in enumerate(statuses):
    status_blocks = checkStatusString(content, status_name)
    if status_blocks:
        if blocks:
            blocks.append(dividerBlock())
        blocks.extend(status_blocks)

#Checks if there's any blocks to run
if blocks:
    runBlocks(blocks)
