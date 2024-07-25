import gspread
import time
from datetime import date
from ss_manip import readCSVFiles
from jolt_scraper_v4 import downloadCSVs
from activeTask_manip import prelim_activeTaskModify, post_activeTaskModify
from google.oauth2.service_account import Credentials


# Test functions
# Set up credentials
#from auth import SERVICE_KEY_JSON_FILE, SPREADSHEET_ID, MASTER_SPREADSHEET_ID
SPREADSHEET_ID = os.environ['SPREADSHEET_ID']
MASTER_SPREADSHEET_ID = os.environ['MASTER_SPREADSHEET_ID']
SERVICE_KEY_JSON_FILE = os.environ['SERVICE_KEY_JSON_FILE']

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
creds = Credentials.from_service_account_info(SERVICE_KEY_JSON_FILE, scopes=SCOPES)
client = gspread.authorize(creds)


print("hello")
time.sleep(5)

#Testing the functions. (Downloads files & lists names of downloaded files)
listName = ["BOH Cleaning List"]
#print("Testing prelim secondary function")
prelim_activeTaskModify(client, SPREADSHEET_ID)
time.sleep(5)

#print("Testing primary functions")
path = downloadCSVs(listName)  
result = readCSVFiles(path, client, SPREADSHEET_ID, MASTER_SPREADSHEET_ID)       #Prints a dictionary of the important data types
time.sleep(5)

#print(result)
post_activeTaskModify(client, SPREADSHEET_ID, result, date(2024,7,31), date(2024,8,20))
