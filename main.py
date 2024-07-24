import os
import gspread
import time
from ss_manip import readCSVFiles
from jolt_scraper_v4 import downloadCSVs
from google.oauth2.service_account import Credentials


# Test functions
from auth import SERVICE_KEY_JSON_FILE, SPREADSHEET_ID, MASTER_SPREADSHEET_ID
'''
        SPREADSHEET_ID = os.environ['SPREADSHEET_ID']
        MASTER_SPREADSHEET_ID = os.environ['MASTER_SPREADSHEET_ID']
        SERVICE_KEY_JSON_FILE = os.environ['SERVICE_KEY_JSON_FILE']
'''
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
creds = Credentials.from_service_account_info(SERVICE_KEY_JSON_FILE, scopes=SCOPES)
client = gspread.authorize(creds)

#Testing the functions. (Downloads files & lists names of downloaded files)
listName = ["BOH Cleaning List".lower()]
path = os.path.dirname(os.path.realpath(__file__)) + '\\tmp'

#Prints a dictionary of the important data types
path = downloadCSVs(listName)
print(readCSVFiles(path, client, SPREADSHEET_ID, MASTER_SPREADSHEET_ID))
