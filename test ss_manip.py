import os
import gspread
import time
from ss_manip import readCSVFiles
from google.oauth2.service_account import Credentials


# Test functions
if __name__ == '__main__':
    try:
        path = os.path.dirname(os.path.realpath(__file__)) + '\\tmp'
        print(path)

        # Set up credentials
        from auth import SERVICE_KEY_JSON_FILE, SPREADSHEET_ID, MASTER_SPREADSHEET_ID
        '''
        SPREADSHEET_ID = os.environ['SPREADSHEET_ID']
        MASTER_SPREADSHEET_ID = os.environ['MASTER_SPREADSHEET_ID']
        SERVICE_KEY_JSON_FILE = os.environ['SERVICE_KEY_JSON_FILE']
        '''
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        creds = Credentials.from_service_account_info(SERVICE_KEY_JSON_FILE, scopes=SCOPES)
        client = gspread.authorize(creds)

        #Prints a dictionary of the important data types
        print(readCSVFiles(path, client, SPREADSHEET_ID, MASTER_SPREADSHEET_ID))

    except gspread.exceptions.APIError as e:
        try:
            time.sleep(4)
            print("Momentairly unable to access Google Sheets API. Will attempt to access again. \n\tPlease wait a few minutes...")
            time.sleep(240) #4 minutes
            print("Second attempt commencing...\n\n")
            readCSVFiles(path)
        except gspread.exceptions.APIError as e:
            print("Still unable to access API. Please check if quota limit has been reached.")
        except FileNotFoundError as e:
            print("The file path '" + path + "' doesn't exist within this system.\nMake sure " + os.path.dirname(os.path.realpath(__file__)) + " has a 'tmp' folder within.")
    except FileNotFoundError as e:
        print("The file path '" + path + "' doesn't exist within this system.\nMake sure " + os.path.dirname(os.path.realpath(__file__)) + " has a 'tmp' folder within.")
    