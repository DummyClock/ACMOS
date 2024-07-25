import pandas as pd
import gspread
import time
from datetime import date
import re
from google.oauth2.service_account import Credentials
from datetime import date, timedelta

# Update all status cells with the labels "DUE" or 'UPCOMING"
def prelim_activeTaskModify(client, ss_id):
    #Fail Safe for API Failure
    api_error = True
    api_error_counter = 3

    #While loop checks for api failure
    print("\nUpdating Statuses in Active-Tasks")
    while api_error and api_error_counter > 0:
        try:
            sheet = client.open_by_key(ss_id).get_worksheet(1) #Get's second sheet
            matches_due = sheet.findall("DUE")
            for cell in matches_due:
                cell.value = "OVERDUE"
            matches_upc = sheet.findall("UPCOMING")
            for cell in matches_upc:
                cell.value = "DUE"
            cells_to_update = matches_due + matches_upc
            if not cells_to_update:
                return
            else:
                sheet.update_cells(cells_to_update)
        except gspread.exceptions.APIError as e:
            # If API Error occurs, reattempt to access Google Sheets API (MAX ATTEMPS = 3)
            api_error = apiTimeOut(api_error_counter)

#Adds new UPCOMING tasks
def post_activeTaskModify(client, ss_id, results, startDate = None, endDate = None):
    #Fail Safe for API Failure
    api_error = True
    api_error_counter = 3

    #While loop checks for api failure
    print("\nStarting post process for Active-Task sheet")
    while api_error and api_error_counter > 0:
        try:
            #Get both sheets
            full_cleaning_sheet = client.open_by_key(ss_id).get_worksheet(0) #Get's main sheet
            active_sheet = client.open_by_key(ss_id).get_worksheet(1) #Get's active-task sheet

            api_error = False

            #If no start date OR end date is passed, autogenerate them
            if startDate == None or endDate == None:
                startDate = date.today() + timedelta(days=7)
                endDate = date.today() + timedelta(days=13)
            print("-Start Date: " + str(startDate))
            print("-End_Date: " + str(endDate))
            endDate_values = str(endDate).split("-")
            startDate_values = str(startDate).split("-")

            #Construct regex and use to find upcoming dates within the Full_Cleaning_Schedule
            subregex = '('
            dateRange = endDate - startDate
            for i in range(dateRange.days + 1):
                d = (startDate +timedelta(days=i)).day
                if d < 10:  # Converts single digit days into 2-digits
                    subregex += ('0'+str(d) + "|")
                else:
                    subregex += (str(d) + "|")
            subregex = subregex[:-1] + ')'
            regex = r"(" + startDate_values[1] + "|" + endDate_values[1] + ")\\-" + subregex + "\\-(" + startDate_values[0] + "|" + endDate_values[0] + ")"
            #print("Regex:", regex)
            criteria_regex = re.compile(regex)

            #Get Area & Tasks for rows with upcoming dates
            list_of_rows = full_cleaning_sheet.get_all_values()
            area_col = list_of_rows[0].index("Area/Descriptor")
            task_col =  list_of_rows[0].index("Task")
            clean_col = list_of_rows[0].index("Next Cleaning Date")
            
            #Collect the upcoming tasks from rows that fall within the range
            upcomingCleaning = [] #List of Lists
            for row in list_of_rows:
                for cell in row:
                    match = re.search(criteria_regex, cell)
                    if match:
                        upcomingCleaning.append([row[area_col], row[task_col], "UPCOMING"])    
                        #index_of_match = row.index(cell)
                        #print(f"\t-Regex Pattern found in '{cell}' at index {index_of_match} in row {row}")
                        break
                        
            #Commit updates
            active_sheet.append_rows(upcomingCleaning, value_input_option="USER_ENTERED")

            #Delete Rows
            print("\nPreparing to remove completed tasks from Active-Task sheet. \n\tPlease wait a minute for the process to start...")
            time.sleep(60)        #wait one minue
            print("Beginning the removing completed item process. Please wait a moment..")
            deleteRows(full_cleaning_sheet.get_all_values(), active_sheet, results)

        except gspread.exceptions.APIError as e:
            # If API Error occurs, reattempt to access Google Sheets API (MAX ATTEMPS = 3)
            api_error = apiTimeOut(api_error_counter)

#Deletes rows that contain data stored within the results container
def deleteRows(updated_list_of_rows, active_sheet, results):
    area_col2 = updated_list_of_rows[0].index("Area/Descriptor")
    task_col2 =  updated_list_of_rows[0].index("Task")
            
    #deletesCommitted = 0
    row_index = len(updated_list_of_rows)
    for row in reversed(updated_list_of_rows):
        if isFound(row[task_col2], row[area_col2], results):
            active_sheet.delete_rows(row_index)
            print("-Confirming Cleaning Task Completed.")
            time.sleep(5)
        row_index -= 1
    print("Process completed. Yay!")


def apiTimeOut(api_error_counter):
    # If API Error occurs, reattempt to access Google Sheets API (MAX ATTEMPS = 3)
    api_error_counter -= 1 
    if api_error_counter > 0: 
        print("Minute Quota for Google Sheets API reached (CLEANING_SPREADSHEET). Will attempt to access again. \n\tPlease wait a moment...\n\tAttempts Left: " + str(api_error_counter))
        time.sleep(66)  
    else:
        print("Unable to Google Sheets API right now. Skipping this process.")
    return True

def isFound(item1, item2, list_of_containers):
    for container_object in list_of_containers:
        #print(item1, item2, container_object)
        if item1 in container_object.values() and item2 in container_object.values():
            return True
    return False
