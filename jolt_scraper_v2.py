from selenium import webdriver 
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from datetime import date, timedelta
import os
import time

from auth import EMAIL, PASSWORD

def getPeriod():
    """
    Calculates and returns the start and end dates of a one-week period ending today.

    This function computes the dates for today and exactly one week ago. It returns
    these dates as strings in the 'YYYY-MM-DD' format, which is the default string
    representation of Python date objects.

    Returns:
        list of str: A list containing two date strings:
            - The first string is the date one week ago.
            - The second string is today's date.

    Example:
        - If today's date is 2024-06-09, this function will return:
            ['2024-06-02', '2024-06-09']
    """
    end_date = date.today()                     #Today
    start_date = end_date - timedelta(days=7)   #Last Week
    return [str(start_date), str(end_date)]

def downloadCSVs(listNames):
    driver = webdriver.Chrome()
    driver.get("https://app.joltup.com/account#/login")
    time.sleep(3)            # Give time for dynamic elements to load  

    driver.find_element(By.ID, "emailAddress").send_keys(EMAIL)
    driver.find_element(By.ID, "password").send_keys(PASSWORD, Keys.ENTER)
    time.sleep(4)

    driver.get("https://app.joltup.com/review/review/listResultsReporting/gridView")
    time.sleep(4)           # Give time for dynamic elements to load 

    period = getPeriod() #Gather the search period

    driver.find_element(By.CLASS_NAME, "date-range-filter").click() #Open up date range picker
    time.sleep(2)

    #Put in the start date
    start_field = driver.find_element(By.ID, "input-start")
    start_field.clear()
    start_field.send_keys(period[0])

    #Put in the end date
    end_field = driver.find_element(By.ID, "input-end")
    end_field.clear()
    end_field.send_keys(period[1])
    time.sleep(2)

    #Find and click on "Done" in the Date-Range picker menu
    buttons = driver.find_element(By.CLASS_NAME, "date-range-menu").find_element(By.CLASS_NAME, "button-row").find_elements(By.CLASS_NAME, "button")
    for button in buttons:
        span_text = button.find_element(By.TAG_NAME, "span").text
        if span_text.lower() == "done":
            button.click()
    time.sleep(5)

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

#Testing the functions.
listName = ["BOH Closing Checklist".lower()]
downloadCSVs(listName)
