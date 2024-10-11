import pandas as pd, gspread, os, time
from google.oauth2.service_account import Credentials
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from gspread.exceptions import APIError, GSpreadException
from gspread import cell

MAX_API_REQUEST = 15
num_of_new_entries = 0

# Will search the downloaded csv files in path for specific values
def readCSVFiles(path, client, ID_OF_SPREADSHEET_TO_EDIT, ID_OF_SPREADSHEET_TO_REFERENCE):
    # Store important results here
    important_results = []
    requestBatch = []

    # Values to search for within the downloaded csv files
    date_value = 'Date of Cleaning Task'
    task_value = 'Cleaning Task'

    #Loop through files in directory
    downloadedFiles = os.listdir(path)
    for f in downloadedFiles:

        # Convert csv file into dataframe & set headers
        file_path = os.path.join(path, f)
        df = pd.read_csv(file_path).T.drop_duplicates()
        new_header = df.iloc[0]  
        df = df[1:]  
        df.columns = new_header  

        # Get Sheet values
        api_e_attempt = 3
        while api_e_attempt > 0:
            try:
                masterWS = client.open_by_key(ID_OF_SPREADSHEET_TO_REFERENCE).sheet1  #'sheet1' refers to the name of the actual sheet
                all_master_values = masterWS.get_all_values()
                cleaningWS = client.open_by_key(ID_OF_SPREADSHEET_TO_EDIT).sheet1
                all_schedule_values = cleaningWS.get_all_values()
                break       # API access was succesful, then bypass the check
            except APIError as e:
                api_e_attempt = api_e_attempt - 1
                if api_e_attempt > 0:
                    print("API ERROR OCCURED! Reattempting to access in 1 minute and 30 seconds...")
                    time.sleep(90)
                else:
                    print("APIError Code: " + f"APIError: {e.response.status_code}")
                    raise Exception("Failed to connect to API at this moment. Please refer to the APIError's documentation: \n\thttps://docs.gspread.org/en/latest/api/exceptions.html")

        # Read each row for specific values
        date_value_col = df.columns.get_loc(date_value)
        task_value_col = df.columns.get_loc(task_value)
        for rows in range(df.shape[0]):
            if rows == 0:
                continue
            date_result = df.iloc[rows,date_value_col].split()
            task_result = df.iloc[rows,task_value_col].split(" - ")

            # Retrieve data for a batch update AND dict of results
            results = searchFrequencyMasterSheet(date_result, task_result, all_master_values, all_schedule_values)
            important_results.append(results[0])
            requestBatch.append(results[1])

        # Commit batch update to cleaning ws
        body = {"requests": requestBatch}
        print(body)        #testing line
        ss = client.open_by_key(ID_OF_SPREADSHEET_TO_EDIT)
        ss.batch_update(body)

    # Return dict
    return removeDupCleaningTasks(important_results)

# Will search the Frequency Master Sheet for specific values
def searchFrequencyMasterSheet(result_date, result_area, all_master_values, all_schedule_values):
    try:
                # Find neccessary column indexs (index values start at 0, when using for gspread functions remember to increment the index)
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
                
                # Get frequency, Reformat date, Calculate next cleaning date
                freq = all_master_values[row_index][freq_col]
                amount = all_master_values[row_index][amount_col]
                date_values = result_date[0].split('/')
                reformatted_date = date_values[0] + '-' + date_values[1] + '-' + date_values[2]
                next_date = calculateNextDate([int(date_values[0]), int(date_values[1]), int(date_values[2])], freq, int(amount))

                return updateCleaningScheduleSheet(reformatted_date, next_date, result_area, all_schedule_values)
    except AttributeError as e:
        print("ERROR 102: Unable to find the 'Task' column,'Area/Descriptor' column, 'Frequency' column, and/or 'Amount' column in the '" + client.open_by_key(MASTER_SPREADSHEET_ID).title + "' Spreadsheet.")
        print(e)
    except TypeError as e:
        print("ERROR 103: Unable to calculate the next cleaning date. Be sure to follow the date syntax 'MM-DD-YYYY'.\n Make sure a proper date is stored in the " + client.open_by_key(MASTER_SPREADSHEET_ID).title + "'Frequency' & 'Amount' columns.")
        print(e)
    except ValueError as e:
        print("ERROR 104: Unable to parse the date collected from the downloaded file.")
        print(e)
    except NameError as e:
        print("ERROR 105: Unable to open the Master Spreadsheet. Please check the Master_Spreadsheet_ID.")
        print(e)

# Updates the cleaning schedule sheet based on the results found in the csv file
def updateCleaningScheduleSheet(reformatted_date, next_date, task__area, all_schedule_values):
        #Find all necessary column indicies
        area_col = all_schedule_values[0].index("Area/Descriptor")
        task_col =  all_schedule_values[0].index("Task")
        last_cleaning_col = all_schedule_values[0].index("Last Cleaning Date") 
        next_cleaning_col = all_schedule_values[0].index("Next Cleaning Date")
        stl_cleaning_col = all_schedule_values[0].index("Second to Last Cleaning Date")

        #Prepare return values
        batch = []
        returnDict = {
            "Area/Descriptor" : task__area[1],
            "Task" : task__area[0],
            "Next Cleaning Date" : next_date,
            "Last Cleaning Date" : reformatted_date,
        }
               
        #Search for the matching row
        found = False
        row_index = 0
        for row_index, row in enumerate(all_schedule_values):
            if row[task_col] == task__area[0] and row[area_col] == task__area[1]:
                found = True
                print("- Found '" + task__area[0] + "' & '" + task__area[1] + "' on Row: " + str(row_index+1) + " of Cleaning Spreadsheet")
                previous_last_date = all_schedule_values[row_index][next_cleaning_col]      #Save the 'outdated' last cleaning date; will use later
                break
                
        # If unable to find, add it to the list (if it's data was found in the Master Spreadsheet)
        if not found:
            print("  - NOT Found in Cleaning Schedule Spreadsheet. Preparing to add a new entry...")
            global num_of_new_entries
            num_of_new_entries = num_of_new_entries + 1
            row_index = row_index + num_of_new_entries
            previous_last_date = ''
        
        #print(reformatted_date, next_date, previous_last_date)
        # Format request to edit the "Last Cleaning Date" column 
        api_error = True
        api_error_counter = 3
        while api_error and api_error_counter > 0:
            try:
                if previous_last_date == '':
                    batch = formatBatch(task__area[1], task__area[0], area_col+1, task_col+1, row_index+1, [last_cleaning_col+1, next_cleaning_col+1], [reformatted_date, next_date])
                else:
                    batch = formatBatch(task__area[1], task__area[0], area_col+1, task_col+1, row_index+1, [last_cleaning_col+1, next_cleaning_col+1, stl_cleaning_col+1], [reformatted_date, next_date, previous_last_date])
                return (returnDict, batch)  
            except (APIError, GSpreadException) as e:
                    # If API Error occurs, reattempt to access Google Sheets API (MAX ATTEMPS = 3)
                    print("Timeout 1")
                    api_error = apiTimeOut(api_error_counter)
                    api_error_counter -= 1   

#date_values: (int)[day, month, year]
def calculateNextDate(date_values, freq, amount):
    constructed_date = datetime(date_values[2], date_values[0], date_values[1])     #Year, Month, Day

    if freq == "Day":
        constructed_date = constructed_date + relativedelta(days=amount)
    elif freq == "Week":
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

# Calls a minute cool down
def apiTimeOut(api_error_counter):
    # If API Error occurs, reattempt to access Google Sheets API (MAX ATTEMPS = 3)
    api_error_counter -= 1 
    if api_error_counter > 0: 
        print("Minute Quota for Google Sheets API reached (CLEANING_SPREADSHEET). Will attempt to access again. \n\tPlease wait a moment...\n\tAttempts Left: " + str(api_error_counter))
        time.sleep(66)  
    else:
        print("Unable to Google Sheets API right now. Skipping this process.")
    return True

# Generates a batch request for an entire row
def formatBatch(area, task, area_col, task_col, row, list_of_cols, list_of_dates):
    requests = []
    requests.append(
        {
            "updateCells": {
                "range": {
                    "startRowIndex": row-1,  
                    "endRowIndex": row,        
                    "startColumnIndex": area_col-1, 
                    "endColumnIndex": area_col,  
                },
                "rows": [
                    {
                        "values": [
                            {
                                "userEnteredValue": {
                                    "stringValue": area
                                }
                            }
                        ]
                    }
                ],
                "fields": "userEnteredValue"
            }
        }
    )
    requests.append(
        {
            "updateCells": {
                "range": {
                    "startRowIndex": row-1,  
                    "endRowIndex": row,        
                    "startColumnIndex": task_col-1, 
                    "endColumnIndex": task_col  
                },
                "rows": [
                    {
                        "values": [
                            {
                                "userEnteredValue": {
                                    "stringValue": task
                                }
                            }
                        ]
                    }
                ],
                "fields": "userEnteredValue"
            }
        }
    )
    for col_index, col in enumerate(list_of_cols):
        d = list_of_dates[col_index].split('-')
        request = {
            "updateCells": {
                "range": {
                    "startRowIndex": row - 1,  
                    "endRowIndex": row,        
                    "startColumnIndex": col-1, 
                    "endColumnIndex": col  
                },
                "rows": [
                    {
                        "values": [
                            {
                                "userEnteredValue": {
                                    "stringValue": list_of_dates[col_index]
                                },
                                "userEnteredFormat": {
                                    "horizontalAlignment": "RIGHT"
                                    }
                            }
                        ]
                    }
                ],
                "fields": "userEnteredValue,userEnteredFormat.horizontalAlignment"
            }
        }
        requests.append(request)
    return requests
"""from auth import SERVICE_KEY_JSON_FILE, SPREADSHEET_ID, MASTER_SPREADSHEET_ID
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
creds = Credentials.from_service_account_info(SERVICE_KEY_JSON_FILE, scopes=SCOPES)
client = gspread.authorize(creds)
path = os.path.dirname(os.path.realpath(__file__)) + '\\tmp'

readCSVFiles(path, client, SPREADSHEET_ID, MASTER_SPREADSHEET_ID)"""
