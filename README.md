# ACMOS: Automated Cleaning & Maintenance Organizer & Scheduler

ACMOS is a project aimed at automating the cleaning and maintenance scheduling process for our workplace. It integrates with Jolt to gather task completion data and sends out reminders and updates through Slack. This ensures that cleaning schedules are adhered to and makes it easier for the team to stay organized.

## Table of Contents
- [Project Description](#project-description)
- [Planned Features](#planned-features)
- [To-Do List](#to-do-list)

## Project Description

ACMOS automates the collection of cleaning task completion data from Jolt and sends reminders and updates via Slack. By utilizing familiar tools like Jolt for task completion and Slack for communication, ACMOS makes it easy for teams to stay on top of their cleaning schedules.

## Planned Features

- Automated data collection from Jolt using Selenium
- Weekly and Day-Of reminders sent via Slack
    - States Upcoming, Due, and Overdue tasks
- Integration with Google Sheets for tracking, and scheduling.
    - Easily accessible and Easy to modify from anywhere

## To-Do List

- Cleanup Repository
    - Remove excess files or move them to an archive folder or archive branch
- Create a main file for running
    - Includes calling methods for downloading data, manipulating data, and sending information to Slack
- ~~Add logging~~ No need for it at this moment
- Update Frequency columns in Master
    - From Frequency in both days and words, use a column for the amount of a frequency and then a column for the frequency(CSV EX: "Primary","Fry Fridge","2","Month"; This'll be every 2 months) 
- Finish CSV/Spreadsheet modification methods
    - ~~Move CSV/Spreadsheet modification methods into their own package/module/file~~
    - ~~Incorporate Cleaning task frequency master list spreadsheet~~
    - ~~Finish method for reading the currently downloaded spreadsheets and properly sending them to the date calculation method~~
    - ~~Create a next-date calculation method, which calculates the next cleaning date and send both the next and current date to Google Spreadsheets~~
    - ~~Method for calculating the next cleaning date returns a dictionary of modified cleaning tasks.~~
    - Gather the tasks coming up within the next month/week, to be sent on Slack as a reminder
    - Spreadsheet named "active-tasks", for storing DUE, OVERDUE, and UPCOMING tasks to be use for Slack
        - Spreadsheet gets updated weekly, Due turns to overdue then removed later using the returned dictionary. UPCOMING turn to DUE, as it's now the week its due.
        - Check if we can both update the active task status as we removed cleaned tasks; Divide & Conquer or All at Once
