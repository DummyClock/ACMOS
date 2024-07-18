from selenium import webdriver 
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from datetime import date, timedelta
from google.oauth2.service_account import Credentials
import gspread
import os
import time
import json


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
    print("Check it:" +SPREADSHEET_ID)

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

    return os.listdir(download_dir)

#Function used to set the date range in Jolt's completed lists in grid view
def dateRange(driver, startDate, endDate):
    driver.find_element(By.CLASS_NAME, "date-range-filter").click() #Open up date range picker
    time.sleep(2)

    #Put in the start date
    start_field = driver.find_element(By.ID, "input-start")
    start_field.clear()
    start_field.send_keys(startDate)
    # Trigger focus event on another element to ensure the dates are registered
    driver.find_element(By.CLASS_NAME, "date-range-picker").click()
    time.sleep(1)

    #Put in the end date
    end_field = driver.find_element(By.ID, "input-end")
    end_field.clear()
    end_field.send_keys(endDate)
    # Trigger focus event on another element to ensure the dates are registered
    driver.find_element(By.CLASS_NAME, "date-range-picker").click()
    time.sleep(1)

    #Find and click on "Done" in the Date-Range picker menu
    buttons = driver.find_element(By.CLASS_NAME, "date-range-menu").find_element(By.CLASS_NAME, "button-row").find_elements(By.CLASS_NAME, "button")
    for button in buttons:
        span_text = button.find_element(By.TAG_NAME, "span").text
        if span_text.lower() == "done":
            button.click()
    time.sleep(5)

#Testing the functions. (Downloads files & lists names of downloaded files)
listName = ["BOH Closing Checklist"]
print("Files: " + str(downloadCSVs(listName)))
# editGoogleSheets("Nugg", "TODAY")
