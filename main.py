import gspread
import time, os
from datetime import date
from ss_manip import readCSVFiles
from jolt_scraper_v4 import downloadCSVs
from activeTask_manip import prelim_activeTaskModify, post_activeTaskModify
from google.oauth2.service_account import Credentials


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
