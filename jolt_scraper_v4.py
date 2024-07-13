from selenium import webdriver 
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from datetime import date, timedelta
from google.oauth2.service_account import Credentials
import gspread
import os
import time
import JSON


# auth import EMAIL, PASSWORD, SPREADSHEET_ID, SERVICE_KEY_JSON_FILE
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# Gets hidden values from Github Secrets - (Remove this block when testing on a locally)
EMAIL = os.environ['EMAIL']
PASSWORD = os.environ['PASSWORD']
SERVICE_KEY_JSON_FILE = json.loads(os.environ['SERVICE_KEY_JSON_FILE'])
SPREADSHEET_ID = os.environ['SPREADSHEET_ID']

def downloadCSVs(listNames, startDate=None, endDate=None):
    #Get the default one-week-period dates
    if startDate == None and endDate == None:
        endDate = str(date.today())
        startDate = str(date.today() - timedelta(days=7))
    print("StartDate:"+startDate+"!")

    #Prepare download location before launching instance of webdriver in headless mode
    download_dir = os.path.dirname(os.path.realpath(__file__))+ '\\tmp'
    
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
        print("Created a temporary directory to store downloads\n\tPath: '" + download_dir +"'")

    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download":False,
        "directory_upgrade":True,
    }

    options = Options()
    options.add_argument("--headless=new")
    options.add_experimental_option("prefs", prefs)

    #Launch webdriver instance
    driver = webdriver.Chrome(options = options)
    driver.get("https://app.joltup.com/account#/login")
    time.sleep(3)            # Give time for dynamic elements to load  

    driver.find_element(By.ID, "emailAddress").send_keys(EMAIL)
    driver.find_element(By.ID, "password").send_keys(PASSWORD, Keys.ENTER)
    time.sleep(4)

    driver.get("https://app.joltup.com/review/review/listResultsReporting/gridView")
    time.sleep(6)           # Give time for dynamic elements to load 

    dateRange(driver, startDate, endDate)

    lowercaseNames = [name.lower() for name in listNames]       #Turns desired lists' names lowercase
    list_of_titles = driver.find_elements(By.CLASS_NAME, "left-column-item-title")  #Gathers all list titles

    #Find desired list and download the CSV file
    for t in list_of_titles:
        title = t.find_element(By.TAG_NAME, "span").text.lower()
        if title in lowercaseNames: 
            t.click()
            time.sleep(3)

            driver.find_element(By.CLASS_NAME, "list-download").click()
            time.sleep(5)

    driver.get("https://app.joltup.com/site/logout")

    time.sleep(1.5)
    driver.close()
    readCSVs(download_dir)

#ISSUE: Correct value is entered, but site does not store it, leaving it to reset
def dateRange(driver, startDate, endDate):
    driver.find_element(By.CLASS_NAME, "date-range-filter").click() #Open up date range picker
    time.sleep(2)

    #Put in the start date
    start_field = driver.find_element(By.ID, "input-start")
    start_field.clear()
    start_field.send_keys(startDate)

    #Put in the end date
    end_field = driver.find_element(By.ID, "input-end")
    end_field.clear()
    end_field.send_keys(endDate)
    time.sleep(2)

    #Find and click on "Done" in the Date-Range picker menu
    buttons = driver.find_element(By.CLASS_NAME, "date-range-menu").find_element(By.CLASS_NAME, "button-row").find_elements(By.CLASS_NAME, "button")
    for button in buttons:
        span_text = button.find_element(By.TAG_NAME, "span").text
        if span_text.lower() == "done":
            button.click()
    time.sleep(5)

#INCOMPLETE: Currently only get's a list of the downloaded files
def readCSVs(path):
    files = os.listdir(path)
    print("Downloaded Files:")
    print(files)

    # From downloaded files, retrieve data for the cleaned item & the date it was cleaned
    item_cleaned = "Nugget Thaw Cabinet"
    date_of_cleaning = "INSERT_DATE"
    editGoogleSheets(item_cleaned, date_of_cleaning)

#INCOMPLETE: Doesn't have a way to calculate the next cleaning date
# Update the Google Sheet with new data
def editGoogleSheets(item_name, last_cleaning_date):
    # Connect to Sheets API & Google Spreadsheet
    creds = Credentials.from_service_account_info(SERVICE_KEY_JSON_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SPREADSHEET_ID).sheet1  #'sheet1' refers to the name of the actual sheet

    # Search for the item name's row, if it doesn't exist add a new row
    try:
        item_row = sheet.find(item_name).row
    except AttributeError as error:
        sheet.append_row([item_name])
        item_row = sheet.find(item_name).row

    # Update "Last Cleaning Date" column 
    try:
        last_cleaning_col = sheet.find("Last Cleaning Date").col
        sheet.update_cell(item_row,last_cleaning_col, last_cleaning_date)
    except AttributeError as error:
        print("ERROR: Unable to find column with the value: 'Last Cleaning Date'")

    # INCOMPLETE: 
    # Update "Next Cleaning Date" column
    try:
        next_cleaning_date = "INSERT NEXT DATE HERE"
        next_cleaning_col = sheet.find("Next Cleaning Date").col
        sheet.update_cell(item_row,next_cleaning_col, next_cleaning_date)
    except AttributeError as error:
        print("ERROR: Unable to find column with the value: 'Next Cleaning Date'")

#Testing the functions. (Downloads files & lists names of downloaded files)
listName = ["BOH Closing Checklist".lower()]
downloadCSVs(listName)
# editGoogleSheets("Nugg", "TODAY")
