# ACMOS: Automated Cleaning & Maintenance Organizer & Scheduler

ACMOS is a project aimed at automating the cleaning and maintenance scheduling process for our workplace. It integrates with Jolt to gather task completion data and sends out reminders and updates through Slack. This ensures that cleaning schedules are adhered to and makes it easier for the team to stay organized.

## Table of Contents
- [Project Description](#project-description)
- [Features](#features)
- [To-Do List](#to-do-list)

## Project Description

ACMOS automates the collection of cleaning task completion data from Jolt and sends reminders and updates via Slack. By utilizing familiar tools like Jolt for task completion and Slack for communication, ACMOS makes it easy for teams to stay on top of their cleaning schedules.

## Features

- Automated data collection from Jolt using Selenium
- Weekly reminders sent via Slack
    - States Upcoming, Due, and Overdue tasks
- Integration with Google Sheets for tracking, and scheduling.
    - Easily accessible and Easy to modify from anywhere

## To-Do List

- Cleanup Repository
    - Remove excess files or move them to an archive folder or archive branch
- Further Testing to ensure it works, and to work out any issues
- Figure out how to handle weekly tasks; May not even be handled within this project, However bi-weekly can be.
  - Spamming the slack channel could result in it being ignored.
  - Accessing Jolt everyday could be accessing it too much.
- Desktop Application for a more user-friendly experience modifying the master, active, and schedule sheets properly and validating the data.
  - Planned 'Stack': React, Electron, 'gsheets', Nodejs.
- Implement an additonal layer to Overdue, which reminds on a slightly more frequent basis 2 or more weeks after the initial due date.
- Run the program at random interval 3 hours prior to 12:00pm, and send slack messages at 12:00pm
- Fix dividers
