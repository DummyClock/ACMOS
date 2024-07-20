import pandas as pd
import gspread
import os
import time
from google.oauth2.service_account import Credentials
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

# Will search the downloaded csv files in path for specific values
def readCSVFiles(path, client, ID_OF_SPREADSHEET_TO_EDIT, ID_OF_SPREADSHEET_TO_REFERENCE):
    # Store important results here
    important_results = []

    # Values to search for within the downloaded csv files
    date_value = 'Date of Cleaning Task'
    task_value = 'Cleaning Task'

    downloadedFiles = os.listdir(path)
    for f in downloadedFiles:
        # Convert into dataframe
        file_path = os.path.join(path, f)
        df = pd.read_csv(file_path).T
        new_header = df.iloc[0]  
        df = df[1:]  
        df.columns = new_header  

        # Read each row for specific values
        date_value_col = df.columns.get_loc(date_value)
        task_value_col = df.columns.get_loc(task_value)
        for rows in range(df.shape[0]):
            result1 = df.iloc[rows,date_value_col].split()
            result2 = df.iloc[rows,task_value_col].split(" - ")
            #print(result1)
            #print(result2)
            important_results.append(searchFrequencyMasterSheet(result1, result2, client, ID_OF_SPREADSHEET_TO_EDIT, ID_OF_SPREADSHEET_TO_REFERENCE))
    return important_results

# Will search the Frequency Master Sheet for specific values
def searchFrequencyMasterSheet(result_date, result_area, client, SPREADSHEET_ID, MASTER_SPREADSHEET_ID):
    try:
        #Fail Safe for API Failure
        api_error = True
        api_error_counter = 0

        #While loop checks for api failure
        while(api_error and api_error_counter <=3):
            try:
                api_error = False
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
                frequency_col_index = sheet.find("Frequency").col       #Frequency
                amount_col_index = sheet.find("Amount").col             #Amount
                freq = sheet.cell(row_index, frequency_col_index).value
                amount = int(sheet.cell(row_index, amount_col_index).value)

                # Calculate the next cleaning date
                if date_values == "":
                    date_values = datetime.today().strftime("%m/%d/%y")
                else:
                    date_values = result_date[0].split('/')
                reformatted_date = date_values[0] + '-' + date_values[1] + '-' + date_values[2]
                next_date = calculateNextDate([int(date_values[0]), int(date_values[1]), int(date_values[2])], freq, amount)

            except gspread.exceptions.APIError as e:
                # If API Error occurs, reattempt to access Google Sheets API (MAX ATTEMPS = 3)
                print("Momentairly unable to access Google Sheets API. Will attempt to access again. \n\tPlease wait a few minutes...")
                time.sleep(180)
                api_error = True
                api_error_counter =+ 1

        # Check if max attempts have been made
        if api_error_counter >= 3:
            print("Maxiumum Attempts (3) have been made! Please try again some other time.")
            return []

        return updateCleaningScheduleSheet(reformatted_date, next_date, result_area, client, SPREADSHEET_ID)
    except AttributeError as e:
        print("ERROR: Unable to find the 'Task' column and/or 'Area/Descriptor' column and/or 'C' column in the '" + client.open_by_key(MASTER_SPREADSHEET_ID).title + "' Spreadsheet.")
    except TypeError as e:
        print("ERROR: Unable to calculate the next cleaning date. Be sure to follow the date syntax 'MM-DD-YYYY'.\n Make sure a proper date is stored in the " + client.open_by_key(MASTER_SPREADSHEET_ID).title + "'Frequency' & 'Amount' columns.")
    except ValueError as e:
        print("ERROR: Unable to parse the date collected from the downloaded file.")
    except NameError as e:
        print("ERROR: Unable to open the Master Spreadsheet. Please check the Master_Spreadsheet_ID.")

# Updates the cleaning schedule sheet based on the results found in the csv file
def updateCleaningScheduleSheet(reformatted_date, next_date, result_area, client, SPREADSHEET_ID):
    try:
        #Fail Safe for API Failure
        api_error = True
        api_error_counter = 0

        #While loop checks for api failure
        while(api_error and api_error_counter <=3):
            try:
                api_error = False
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
            except gspread.exceptions.APIError as e:
                # If API Error occurs, reattempt to access Google Sheets API (MAX ATTEMPS = 3)
                print("Momentairly unable to access Google Sheets API. Will attempt to access again. \n\tPlease wait a few minutes...")
                time.sleep(180)
                api_error = True
                api_error_counter =+ 1

        # Check if max attempts have been made
        if api_error_counter >= 3:
            print("Maxiumum Attempts (3) have been made! Please try again some other time.")
            return []
        
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

    #Returns a dictionary of the important data
    return {
        "Area/Descriptor" : result_area[1],
        "Task" : result_area[0],
        "Next Cleaning Date" : next_date,
        "Last Cleaning Date" : reformatted_date,
    }

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

    return str(constructed_date).split()[0]
