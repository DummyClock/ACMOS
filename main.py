import gspread, time, os
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
    elif "Jet Plates" in task:
        task = "Oven " + task
    elif "#" in task:
        #Split task name between the descriptor and everything else
        descriptor, rest_of_name = task.split(' ', 1)

        #Find the first occurence of the specified phrase, and insert descriptor
        if "Oven" in rest_of_name:
            object_name, rest = rest_of_name.split("Oven", 1)
            task = f"{object_name}Oven {descriptor}{rest}"
        elif "Toaster" in rest_of_name:
            object_name, rest = rest_of_name.split("Toaster", 1)
            task = f"{object_name}Toaster {descriptor}{rest}"
    return task

#Checks a Status' output string to see if a task exists there
def checkStatusString(string, stringName, blockList,divider=True):
    if len(string) > 0:
        if divider == True:
            return blockList.extend([headerBlock(stringName), markdownBlock(string), dividerBlock()])
        else:
            return blockList.extend([headerBlock(stringName), markdownBlock(string)])

# Set up credentials and other Variables
#from auth import SERVICE_KEY_JSON_FILE, SPREADSHEET_ID, MASTER_SPREADSHEET_ID
SPREADSHEET_ID = os.environ['SPREADSHEET_ID']
MASTER_SPREADSHEET_ID = os.environ['MASTER_SPREADSHEET_ID']
SERVICE_KEY_JSON_FILE = os.environ['SERVICE_KEY_JSON_FILE']

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
creds = Credentials.from_service_account_info(SERVICE_KEY_JSON_FILE, scopes=SCOPES)
client = gspread.authorize(creds)

listNames = ["BOH Cleaning List"]

#Update Status Codes of tasks in Active Task Spreadsheet
prelim_activeTaskModify(client, SPREADSHEET_ID)
time.sleep(5)

#Download Completed Jolt List Data
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

#Check if there are any blocks to send for each status
blocks = checkStatusString(overdue, "OVERDUE", blocks)
blocks = checkStatusString(due, "DUE", blocks)
blocks = checkStatusString(upcoming, "UPCOMING", blocks)
blocks = checkStatusString(errored, "INVALID STATUS", blocks, divider=False)

#Checks if there's any blocks to run
if len(blocks) != 0:
    runBlocks(blocks)