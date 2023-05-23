The provided code is a Python script that demonstrates the use of the Jira API and MySQL database to manage Jira tickets and executes Task 2 of my project. Here is a description of the code:

   1.The code begins by importing the necessary libraries, including tkinter for creating a GUI, base64 for encoding credentials, requests for making API requests, json for working with JSON data, and mysql.connector for interacting with a MySQL database.

   2. The Jira class is defined, which represents the Jira ticket management functionality. It has an __init__ method that initializes the class and sets up the GUI using tkinter.

   3. Within the Jira class, there are methods for retrieving Jira tickets, navigating through pages, getting tickets from the database, retrieving all Jira tickets, and changing the status of a ticket.

   4. The get_issues method is used to retrieve Jira tickets based on a JQL query. It makes multiple API requests to fetch all the tickets and returns a list of issues.

   5. The show_previous_page and show_next_page methods handle the navigation between pages of tickets in the GUI.

   6. The get_tickets_from_database method retrieves tickets from the MySQL database based on the page number and results per page. It updates the GUI to display the retrieved tickets.

   7. The get_all_jira_tickets method retrieves all Jira tickets using the Jira API and inserts them into the MySQL database.

   8. The change_ticket_status method changes the status of a ticket from 'Open' to 'Close' and adds a comment in Jira using the API. It makes a POST request to the Jira API endpoint for updating an issue.

   9. The code creates a Tkinter root window, initializes a Jira object with the root window as a parameter, and starts the Tkinter event loop.

   10. Another Tkinter root window is created, and another Jira object is initialized with the new root window.

   11. The get_issues, show_previous_page, show_next_page, get_tickets_from_database, get_all_jira_tickets methods are called to demonstrate their functionality.

   12. Finally, the change_ticket_status method is called to change the status of a ticket with the key 'PAK-6' to 'Close' and add a comment.

