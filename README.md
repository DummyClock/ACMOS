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
- Update the current Jolt checklist to include all tasks
   - Maybe we could automate this in some fashion?
- Figure out how to handle weekly tasks; May not even be handled within this project, However bi-weekly can be.
  - Spamming the slack channel could result in it being ignored.
  - Accessing Jolt everyday could be accessing it too much.
