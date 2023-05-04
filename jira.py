#Importing necessary libraries
import tkinter as tk
import base64
import requests
import json
from requests.auth import HTTPBasicAuth
import mysql.connector

class Jira:
    """
    This is a Jira class that provides methods to retrieve and manage Jira tickets.
    """
    def __init__(self, master):
        """
        This method initializes the Jira class.
        :param master: The root tkinter object.
        """
        self.master = master
        self.master.title("Jira Ticket Management")

        # Jira credentials
        self.jira_url = 'https://pakrashi.atlassian.net/rest/api/3/search'
        self.gmail = 'pakrashimadhura@gmail.com'
        self.jira_user = 'madhura123'
        self.jira_api_token = 'ATATT3xFfGF0LpS01iVFUs5cQ9PnB9ccQFLYg5VLRXNi-RRemdcWnRrqImgs8N-XTgFoZ0Pnjf4k-PMBUAZpJgCVdxylEQyOxcPCIHoqUZaPdqh7oeOuuU8zGMybxSzVFNfphbjv2AzWSvaEw8jjPLRPxI7TVsl6Bvtp59W1LLy1rhOJsg_xS_k=0432272D'
        self.header = {"Accept": "application/json",
                       "Content-Type": "application/json",
                       "Authorization": "Basic " + base64.b64encode(
                           f"{self.jira_user}:{self.jira_api_token}".encode()).decode()}
        self.auth = HTTPBasicAuth(self.gmail, self.jira_api_token)

        # Connect to the MySQL database
        try:
            self.mysqldb = mysql.connector.connect(
                user='root',
                password='pakrashimadhura@23',
                host='localhost',
                database='jiratickets'
            )
            self.mycursor = self.mysqldb.cursor(buffered=True)

        except Exception as e:
            print("My database is not connected", e)

        # Create tkinter objects
        self.label = tk.Label(master, text="Jira Ticket Management")
        self.label.pack()

        self.get_tickets_button = tk.Button(master, text="Get Tickets", command=self.get_tickets_from_database)
        self.get_tickets_button.pack()

        self.refresh_button = tk.Button(master, text="Refresh Tickets", command=self.get_all_jira_tickets)
        self.refresh_button.pack()

        self.quit_button = tk.Button(master, text="Quit", command=master.quit)
        self.quit_button.pack()

    def get_tickets_from_database(self):
        """
        This method retrieves tickets from the MySQL database and prints them to the console.
        """
        self.mycursor.execute("select * from tickets_table")
        myresult = self.mycursor.fetchall()

        for x in myresult:
            print(x)

    def get_all_jira_tickets(self):
        """
        This method retrieves all Jira tickets and inserts them into the MySQL database.
        """
        data = []
        response = requests.request("get", self.jira_url, headers=self.header, auth=self.auth)
        tickets = json.loads(response.text)
        all_issues = tickets["issues"]

        for issue in all_issues:
            date = issue["fields"]["updated"].split("T")
            created_date = issue["fields"]["created"].split("T")
            dict_obj = {"Tickets_key": issue["key"], "Title": issue["fields"]["summary"],
                        "Project_name": issue["fields"]["project"]["name"],
                        "Priority": issue["fields"]["priority"]["name"],
                        "Updated_date": date[0], "Ticket_status": issue["fields"]["status"]["name"],
                        "Creator_email": issue["fields"]["creator"]["emailAddress"], "Created_date": created_date[0]}
            data.append(dict_obj)

        for row in data:
            sql = "INSERT INTO tickets_table (Tickets_key, Title, Project_name, Priority, Updated_date, Ticket_status, Creator_email, Created_date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE Tickets_key=VALUES(Tickets_key), Title=VALUES(Title), Project_name=VALUES(Project_name), Priority=VALUES(Priority), Updated_date=VALUES(Updated_date), Ticket_status=VALUES(Ticket_status), Creator_email=VALUES(Creator_email), Created_date=VALUES(Created_date)"
            val = (
                row['Tickets_key'],
                row['Title'],
                row['Project_name'],
                row['Priority'],
                row['Updated_date'],
                row['Ticket_status'],
                row['Creator_email'],
                row['Created_date']
            )

            try:
                self.mycursor.execute(sql, val)
                self.mysqldb.commit()
            except Exception as e:
                print('Your program has an error', e)

        self.mycursor.close()

# Create a Tkinter root window
root = tk.Tk()
# Create a Jira object and pass the root window as a parameter to its constructor
app = Jira(master=root)
# Start the Tkinter event loop
root.mainloop()
# Create another Jira object and pass the root window as a parameter to its constructor
obj = Jira(master=root)
# Call the get_tickets_from_database method of the Jira object to retrieve tickets from the database
obj.get_tickets_from_database()
# Call the get_all_jira_tickets method of the Jira object to retrieve all Jira tickets
obj.get_all_jira_tickets()


