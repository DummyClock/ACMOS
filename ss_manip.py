import pandas as pd
import gspread
import os
import time
from google.oauth2.service_account import Credentials
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from gspread.exceptions import APIError
from gspread import cell

MAX_API_REQUEST = 15

# Will search the downloaded csv files in path for specific values
def readCSVFiles(path, client, ID_OF_SPREADSHEET_TO_EDIT, ID_OF_SPREADSHEET_TO_REFERENCE):
    # Store important results here
    important_results = []

    # Values to search for within the downloaded csv files
    date_value = 'Date of Cleaning Task'
    task_value = 'Cleaning Task'

    #Loop through files in directory
    downloadedFiles = os.listdir(path)
    for f in downloadedFiles:

        # Convert csv file into dataframe
        file_path = os.path.join(path, f)
        df = pd.read_csv(file_path).T
        new_header = df.iloc[0]  
        df = df[1:]  
        df.columns = new_header  

        # Read each row for specific values
        date_value_col = df.columns.get_loc(date_value)
        task_value_col = df.columns.get_loc(task_value)
        api_request = 0
        for rows in range(df.shape[0]):
            result1 = df.iloc[rows,date_value_col].split()
            result2 = df.iloc[rows,task_value_col].split(" - ")
            important_results.append(searchFrequencyMasterSheet(result1, result2, client, ID_OF_SPREADSHEET_TO_EDIT, ID_OF_SPREADSHEET_TO_REFERENCE))
            api_request += 1
            if api_request > MAX_API_REQUEST:
                print("Too many API request made. Taking a quick minute break...")
                api_request = 0
                time.sleep(60)
        # # testing: os.remove(file_path) Delete file
    return removeDupCleaningTasks(important_results)

# Will search the Frequency Master Sheet for specific values
def searchFrequencyMasterSheet(result_date, result_area, client, SPREADSHEET_ID, MASTER_SPREADSHEET_ID):
    try:
        #Fail Safe for API Failure
        api_error = True
        api_error_counter = 3

        #While loop checks for api failure
        while api_error and api_error_counter > 0:
            try:
                # Connect to Sheets API & Google Spreadsheet
                api_error = False   # Prevent unneccessary looping when an error doesn't occur
                sheet = client.open_by_key(MASTER_SPREADSHEET_ID).sheet1  #'sheet1' refers to the name of the actual sheet

                # Find neccessary column indexs (index values start at 0, when using for gspread functions remember to increment the index)
                all_master_values = sheet.get_all_values()
                area_col = all_master_values[0].index("Area/Descriptor")
                task_col =  all_master_values[0].index("Task")
                freq_col = all_master_values[0].index("Frequency")
                amount_col = all_master_values[0].index("Amount")
                
                # Search for the row containing desired "Area" & "Task" values
                found = False
                row_index = 0
                for row_index, row in enumerate(all_master_values):
                    if row[task_col] == result_area[0] and row[area_col] == result_area[1]:
                        found = True
                        print("- Found '" + result_area[0] + "' & '" + result_area[1] + "' on Row: " + str(row_index+1) + " of Master Spreadsheet")
                        break

                # If the row couldn't be found, abort
                if(not found):
                    print("ERROR 101: Unable to find BOTH '" + result_area[0] + "' AND '" + result_area[1] + "' in the " + client.open_by_key(MASTER_SPREADSHEET_ID).title)
                    return
                
                # Calculate the next cleaning date
                freq = all_master_values[row_index][freq_col]
                amount = all_master_values[row_index][amount_col]
            
                date_values = result_date[0].split('/')
                reformatted_date = date_values[0] + '-' + date_values[1] + '-' + date_values[2]

                next_date = calculateNextDate([int(date_values[0]), int(date_values[1]), int(date_values[2])], freq, int(amount))
            except APIError as e:
                # If API Error occurs, reattempt to access Google Sheets API (MAX ATTEMPS = 3)
                api_error = apiTimeOut(api_error_counter)
        return updateCleaningScheduleSheet(reformatted_date, next_date, result_area, client, SPREADSHEET_ID)

    except AttributeError as e:
        print("ERROR 102: Unable to find the 'Task' column,'Area/Descriptor' column, 'Frequency' column, and/or 'Amount' column in the '" + client.open_by_key(MASTER_SPREADSHEET_ID).title + "' Spreadsheet.")
    except TypeError as e:
        print("ERROR 103: Unable to calculate the next cleaning date. Be sure to follow the date syntax 'MM-DD-YYYY'.\n Make sure a proper date is stored in the " + client.open_by_key(MASTER_SPREADSHEET_ID).title + "'Frequency' & 'Amount' columns.")
    except ValueError as e:
        print("ERROR 104: Unable to parse the date collected from the downloaded file.")
    except NameError as e:
        print("ERROR 105: Unable to open the Master Spreadsheet. Please check the Master_Spreadsheet_ID.")

# Updates the cleaning schedule sheet based on the results found in the csv file
def updateCleaningScheduleSheet(reformatted_date, next_date, result_area, client, SPREADSHEET_ID):
    try:
        #Fail Safe for API Failure
        api_error = True
        api_error_counter = 3

        #While loop checks for api failure
        while api_error and api_error_counter > 0:
            try:
                # Modify second Google Sheet
                api_error = False
                sheet2 = client.open_by_key(SPREADSHEET_ID).sheet1

                #Return Value
                returnDict = {
                    "Area/Descriptor" : result_area[1],
                    "Task" : result_area[0],
                    "Next Cleaning Date" : next_date,
                    "Last Cleaning Date" : reformatted_date,
                }

                # Find all necessary column indicies
                all_schedule_values = sheet2.get_all_values()
                area_col = all_schedule_values[0].index("Area/Descriptor")
                task_col =  all_schedule_values[0].index("Task")
                last_cleaning_col = all_schedule_values[0].index("Last Cleaning Date") 
                next_cleaning_col = all_schedule_values[0].index("Next Cleaning Date")
                stl_cleaning_col = all_schedule_values[0].index("Second to Last Cleaning Date")
               
                #When using get_all_values() the indexing starts at 0, so we have to account for it
                batch = []
                found = False
                row_index = 0
                for row_index, row in enumerate(all_schedule_values):
                    if row[task_col] == result_area[0] and row[area_col] == result_area[1]:
                        found = True
                        print("- Found '" + result_area[0] + "' & '" + result_area[1] + "' on Row: " + str(row_index+1) + " of Cleaning Spreadsheet")
                        break
                
                # If unable to find, add it to the list (because it's data was found in the Master Spreadsheet)
                if not found:
                    #batch.append({'range': cell.Cell(row_index, area_col).address, 'values': result_area[1]},{'range': cell.Cell(row_index, task_col).address, 'values': result_area[0]})
                    sheet2.append_row([result_area[1], result_area[0], next_date, reformatted_date])
                    return returnDict

                #Save the 'outdated' last cleaning date; will use later
                previous_last_date = all_schedule_values[row_index][next_cleaning_col]

                # Update for gspread usage
                row_index += 1 
                last_cleaning_col += 1
                next_cleaning_col += 1
                stl_cleaning_col += 1

            except APIError as e:
                # If API Error occurs, reattempt to access Google Sheets API (MAX ATTEMPS = 3)
                api_error = apiTimeOut(api_error_counter)
    except NameError as e:
        print("ERROR 108: Unable to open the Cleaning Schedule Spreadsheet. Please check the Spreadsheet_ID.")

    # Update the "Last Cleaning Date" column with the new date
    batch = formatBatch(row_index, [last_cleaning_col, next_cleaning_col, stl_cleaning_col], [reformatted_date, next_date, previous_last_date])
    sheet2.batch_update(batch, value_input_option="RAW")

    #Returns a dictionary of the important data
    return returnDict

#date_values: (int)[day, month, year]
def calculateNextDate(date_values, freq, amount):
    constructed_date = datetime(date_values[2], date_values[0], date_values[1])     #Year, Month, Day

    if freq == "Week":
        constructed_date = constructed_date + relativedelta(weeks=amount)
    elif freq == "Month":
        constructed_date = constructed_date + relativedelta(months=amount)
    elif freq == "Quarter":
        constructed_date = constructed_date + relativedelta(months=(4*amount))
    else:
        print("'" + freq + "' is an unsuported frequency type. Please use 'Week', 'Month', or 'Quarter' within the 'Frequency' column of the Master Spreadsheet.")
        return "UNABLE TO CALCULATE. Check 'Frequency' column."
    date_values = str(constructed_date).split()[0].split("-")

    return date_values[1] + "-" + date_values[2] + "-" + date_values[0]

# Removes a cleaning task that has a more recent date
def removeDupCleaningTasks(list_of_dictionaries):
    for dic in list_of_dictionaries:
        for d in list_of_dictionaries:
            if dic.values() == d.values():
                continue
            elif dic["Area/Descriptor"] in d.values() and dic["Task"] == d.values():
                list_of_dictionaries.remove(dic)
                continue
    #print(len(list_of_dictionaries))
    return list_of_dictionaries

def isFound(item1, item2, list_of_containers):
    for container_object in list_of_containers:
        if item1 in container_object.values() and item2 in container_object.values():
            return True
    return False

def apiTimeOut(api_error_counter):
    # If API Error occurs, reattempt to access Google Sheets API (MAX ATTEMPS = 3)
    api_error_counter -= 1 
    if api_error_counter > 0: 
        print("Minute Quota for Google Sheets API reached (CLEANING_SPREADSHEET). Will attempt to access again. \n\tPlease wait a moment...\n\tAttempts Left: " + str(api_error_counter))
        time.sleep(66)  
    else:
        print("Unable to Google Sheets API right now. Skipping this process.")
    return True

def formatBatch(row, columns, values):
    a1_notation = {}
    for i in range(len(columns)):
        a1_notation[cell.Cell(row, columns[i]).address] = values[i]
    return [{'range': c, 'values':[[value]]} for c, value in a1_notation.items()]

"""from auth import SERVICE_KEY_JSON_FILE, SPREADSHEET_ID, MASTER_SPREADSHEET_ID
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
creds = Credentials.from_service_account_info(SERVICE_KEY_JSON_FILE, scopes=SCOPES)
client = gspread.authorize(creds)
path = os.path.dirname(os.path.realpath(__file__)) + '\\tmp'

readCSVFiles(path, client, SPREADSHEET_ID, MASTER_SPREADSHEET_ID)"""
