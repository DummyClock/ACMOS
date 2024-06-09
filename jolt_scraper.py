from selenium import webdriver 
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from datetime import date
import os
import time

from auth import EMAIL, PASSWORD

# Concern: Gridview searches list completed this month, so what happens if yesterday was the last day of the month
def getDate():
    months = {
        1: "January",
        2: "February",
        3: "March",
        4: "April",
        5: "May",
        6: "June",
        7: "July",
        8: "August",
        9: "September",
        10: "October",
        11: "November",
        12: "December",
    }
    today_date = date.today() # Concern: Gridview searches list completed this month, so what happens if yesterday was the last day of the month
    return months.get(today_date.month) + " " + str(today_date.day) + ", " + str(today_date.year)

driver = webdriver.Chrome()
driver.get("https://app.joltup.com/account#/login")
time.sleep(3)            # Give time for dynamic elements to load  

desired_list = "listName"

driver.find_element(By.ID, "emailAddress").send_keys(EMAIL)
driver.find_element(By.ID, "password").send_keys(PASSWORD, Keys.ENTER)
time.sleep(4)

driver.get("https://app.joltup.com/review/review/listResultsReporting/listDetails")
time.sleep(4)           # Give time for dynamic elements to load 

formatted_date = getDate()
list_of_titles = driver.find_elements(By.CLASS_NAME, "left-column-item-title")

for t in list_of_titles:
    if t.text == desired_list: 
        t.click()
        time.sleep(3)
        # list_submitted_date = driver.find_element(By.XPATH, '//div[text()="Complete:"]/parent::*').text.split('\n')
        # print(t.find_element(By.XPATH, "./parent::*/parent::*").find_elements(By.CLASS_NAME, "timestamp"))

        for p in t.find_element(By.XPATH, "./parent::*/parent::*").find_elements(By.CLASS_NAME, "timestamp"):
            if p.text.split('\n')[0] == "Complete:" and p.text.split('\n')[1]  == formatted_date:
                driver.find_element(By.CLASS_NAME, 'list-download').click() # download csv file
driver.get("https://app.joltup.com/site/logout")

time.sleep(1.5)
driver.close()
