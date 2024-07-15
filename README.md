# ACMOS: Automated Cleaning & Maintenance Organizer & Scheduler

ACMOS is a project aimed at automating the cleaning and maintenance scheduling process for your workplace. It integrates with Jolt to gather task completion data and sends out reminders and updates through Slack. This ensures that cleaning schedules are adhered to and makes it easier for the team to stay organized.

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
    - Remove excess files, and separate methods/functions into appropriate files/modules/packages
- Create a main file for running
    - Includes calling methods for downloading data, manipulating data, and sending information to Slack
- Add logging
- Finish CSV/Spreadsheet modification methods
    - Move CSV/Spreadsheet modification methods into their own package/module/file
    - Incorporate Cleaning task frequency master list spreadsheet
    - Finish method for reading the currently downloaded spreadsheets and properly sending them to the date calculation method
    - Create a next-date calculation method, which calculates the next cleaning date and send both the next and current date to Google Spreadsheets
    - Store the completed task, date, next date, and who completed it locally to be sent to Slack.
    - Gather the tasks coming up within the next month/week, to be sent on Slack as a reminder