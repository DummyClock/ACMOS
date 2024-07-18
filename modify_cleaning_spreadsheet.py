import pandas as pd
import gspread
import os
import time
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta

# from auth import SERVICE_KEY_JSON_FILE, SPREADSHEET_ID, MASTER_SPREADSHEET_ID

SPREADSHEET_ID = os.environ['SPREADSHEET_ID']
MASTER_SPREADSHEET_ID = os.environ['MASTER_SPREADSHEET_ID']
SERVICE_KEY_JSON_FILE = os.environ['SERVICE_KEY_JSON_FILE']

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
creds = Credentials.from_service_account_info(SERVICE_KEY_JSON_FILE, scopes=SCOPES)
client = gspread.authorize(creds)

# Will search the downloaded csv files in path for specific values
def readCSVFiles(path):
    downloadedFiles = os.listdir(path)
    for f in downloadedFiles:
        #Values to search for in csv files
        date_value = 'DATE-Date of Cleaning Task'
        task_value = 'MULTIPLE_CHOICE-Cleaning Task'

        #Construct file path
        file_path = os.path.join(path, f)

        #Check if file is .csv, then create dataframe
        if not file_path.endswith('.csv'):
            print("ERROR: Cannot open the file '" + os.path.basename(file_path) + "' missing the '.csv' extension")
            continue
        df = pd.read_csv(file_path)
        print("\nFile being parsed: " + os.path.basename(file_path))
        
        #Get the cleaning date from dataframe
        date_row_index = df.index[df['Item'] == date_value].tolist() 
        if not date_row_index:
            print("ERROR: Unable to find the column header '" + date_value + "' in the '" + os.path.basename(file_path) + "' file. Verify that '" + date_value +"' header exists.")
            continue
        else:
            result1 = df.loc[date_row_index, "Result"].to_string(index=False).split()

        #Get the item cleaned fromdataframe
        task_row_index = df.index[df['Item'] == task_value].to_list()
        if not task_row_index:
            print("ERROR: Unable to find the column header '" + task_value + "' in the '" + os.path.basename(file_path) + "' file. Verify that '" + task_value +"' header exists.")
            continue
        else:
            result2 = df.loc[task_row_index, "Result"].to_string(index=False).split(' - ')

        searchFrequencyMasterSheet(result1, result2)

# Will search the Frequency Master Sheet for specific values
def searchFrequencyMasterSheet(result_date, result_area):
    try:
        # Connect to Sheets API & Google Spreadsheet
        sheet = client.open_by_key(MASTER_SPREADSHEET_ID).sheet1  #'sheet1' refers to the name of the actual sheet

        # Find the row with the values in the results list
        task_index = sheet.find("Task").col                          #Task
        area_index = sheet.find("Area/Descriptor").col               #Area/Descriptor
        
        found = False
        row_index = 0
        for row_index, row in enumerate(sheet.get_all_values()):
            if row[task_index-1] == result_area[0] and row[area_index-1] == result_area[1]:
                found = True
                row_index = row_index + 1
                print("- Found '" + result_area[0] + "' & '" + result_area[1] + "' on Row: " + str(row_index) + " of Master Spreadsheet")
                break

        # If the row couldn't be found, abort
        if(not found):
            print("ERROR: Unable to find BOTH '" + result_area[0] + "' AND '" + result_area[1] + "' in the " + client.open_by_key(MASTER_SPREADSHEET_ID).title)
            return
        
        # Get the frequency
        frequency_col_index = sheet.find("Frequency (Days)").col      #Frequency
        freq = int(sheet.cell(row_index, frequency_col_index).value)

        # Calculate the next cleaning date
        date_values = result_date[0].split('/')
        reformatted_date = date_values[0] + '-' + date_values[1] + '-' + date_values[2]
        next_date = str(datetime.now() + timedelta(days=freq)).split()[0]

        updateCleaningScheduleSheet(reformatted_date, next_date, result_area)
    except AttributeError as e:
        print("ERROR: Unable to find the 'Task' column and/or 'Area/Descriptor' column and/or 'C' column in the '" + client.open_by_key(MASTER_SPREADSHEET_ID).title + "' Spreadsheet.")
    except TypeError as e:
        print("ERROR: Unable to calculate the next cleaning date. Make sure a proper integer is stored in the " + client.open_by_key(MASTER_SPREADSHEET_ID).title + "'Frequency (Days)' columns.")
    except ValueError as e:
        print("ERROR: Unable to parse the date collected from the downloaded file.")
    except NameError as e:
        print("ERROR: Unable to open the Master Spreadsheet. Please check the Master_Spreadsheet_ID.")

# Updates the cleaning schedule sheet based on the results found in the csv file
def updateCleaningScheduleSheet(reformatted_date, next_date, result_area):
    try:
        # Modify second Google Sheet
        sheet2 = client.open_by_key(SPREADSHEET_ID).sheet1

        # Find the row with the values in the results list
        task_index = sheet2.find("Task").col                          #Task
        area_index = sheet2.find("Area/Descriptor").col               #Area/Descriptor

        #When using get_all_values() the indexing starts at 0, so we have to account for it
        found = False
        row_index = 0
        for row_index, row in enumerate(sheet2.get_all_values()):
            if row[task_index-1] == result_area[0] and row[area_index-1] == result_area[1]:
                found = True
                row_index = row_index + 1
                print("- Found '" + result_area[0] + "' & '" + result_area[1] + "' on Row: " + str(row_index+1) + " of Cleaning Spreadsheet")
                break

        if(not found):
            print("ERROR: Unable to find BOTH '" + result_area[0] + "' AND '" + result_area[1] + "' in the " + client.open_by_key(SPREADSHEET_ID).title)
            return

    except AttributeError as e:
        print("ERROR: Unable to find the 'Task' column and/or 'Area/Descriptor' column and/or 'C' column in the '" + client.open_by_key(SPREADSHEET_ID).title + "' Spreadsheet.")
    except NameError as e:
        print("ERROR: Unable to open the Cleaning Schedule Spreadsheet. Please check the Spreadsheet_ID.")

    # Update the "Last Cleaning Date" column with the new date
    try:
        last_cleaning_col = sheet2.find("Last Cleaning Date").col
        previous_last_date = sheet2.cell(row_index,last_cleaning_col).value
        sheet2.update_cell(row_index,last_cleaning_col, reformatted_date)
    except AttributeError as error:
        print("ERROR: Unable to find column with the value: 'Last Cleaning Date'")

    # Update "Next Cleaning Date" column with the new date
    try:
        next_cleaning_col = sheet2.find("Next Cleaning Date").col
        sheet2.update_cell(row_index,next_cleaning_col, next_date)
    except AttributeError as error:
        print("ERROR: Unable to find column with the value: 'Next Cleaning Date'")

    try:
        next_cleaning_col = sheet2.find("Second to Last Cleaning Date").col
        sheet2.update_cell(row_index,next_cleaning_col, previous_last_date)
    except AttributeError as error:
        print("ERROR: Unable to find column with the value: 'Second to Last Cleaning Date'")


# Test functions
if __name__ == '__main__':
    try:
        path = os.path.dirname(os.path.realpath(__file__)) + '\\tmp'
        print(path)
        readCSVFiles(path)
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
    
