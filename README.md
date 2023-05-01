# MadgicalTechdom_Project

This Python code defines a class called "Jira" and performs the following tasks:

1.Connects to a MySQL database, retrieves data from a table called "tickets_table" and prints the data.

2.Sends an HTTP GET request to the Jira REST API to fetch a list of Jira tickets.

3.Extracts information about each ticket from the response JSON data, such as the ticket's key, summary, project name, priority, updated date, status, creator email, and created date.

4.Inserts the extracted ticket information into the "tickets_table" table in the MySQL database.

5.Closes the MySQL database connection.

The code aims to fetch data from the Jira API and store it in a MySQL database for further analysis.
