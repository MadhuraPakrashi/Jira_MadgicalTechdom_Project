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
            if self.mysqldb.is_connected():
                print("Database connection established successfully.")
                self.mycursor = self.mysqldb.cursor(buffered=True)
            else:
                print("Failed to connect to the database.")

        except mysql.connector.Error as e:
            print("Error while connecting to MySQL", e)

        # Create tkinter objects
        self.label = tk.Label(master, text="Jira Ticket Management")
        self.label.pack()

        self.get_tickets_button = tk.Button(master, text="Get Tickets", command=self.get_tickets_from_database)
        self.get_tickets_button.pack()

        self.refresh_button = tk.Button(master, text="Refresh Tickets",
                                        command=lambda: [self.get_all_jira_tickets(), self.get_tickets_from_database()])
        self.refresh_button.pack()

        self.tickets_listbox = tk.Listbox(master, height=300, width=300)
        self.tickets_listbox.pack()

        self.quit_button = tk.Button(master, text="Quit", command=master.quit)
        self.quit_button.pack()

    def get_issues(self, jql, max_results=20, start_at=0):
        issues = []
        total = None
        while total is None or start_at < total:
            params = {
                    'jql': jql,
                    'maxResults': max_results,
                    'startAt': start_at
                }
            response = requests.get(self.jira_url, params=params, headers=self.header, auth=self.auth)
            if response.status_code == 200:
                data = json.loads(response.text)
                issues.extend(data['issues'])
                total = data['total']
                start_at += max_results
            else:
                print(f"Error fetching issues: {response.status_code} {response.text}")
                break
        return issues

    def get_tickets_from_database(self, page_number=1, results_per_page=5):
        """
        This method retrieves tickets from the MySQL database based on the page number and results per page,
        and displays them in the GUI window.
        """
        start_index = (page_number - 1) * results_per_page
        end_index = start_index + results_per_page

        # Get the total number of tickets in the database
        self.mycursor.execute("SELECT COUNT(*) FROM tickets_table")
        total_tickets = self.mycursor.fetchone()[0]

        # Clearing the current listbox content
        self.tickets_listbox.delete(0, tk.END)

        if start_index >= total_tickets:
            # If the starting index is greater than or equal to the total number of tickets, there are no more tickets to display
            self.tickets_listbox.insert(tk.END, "No more tickets to display.")
        else:
            # Limit the query to the specified page number and results per page
            self.mycursor.execute(f"SELECT * FROM tickets_table LIMIT {start_index}, {results_per_page}")
            myresult = self.mycursor.fetchall()

            # Inserting each row of data into the listbox
            for row in myresult:
                # Joining the row into a string to insert into the listbox
                row_str = " | ".join(str(r) for r in row)
                self.tickets_listbox.insert(tk.END, row_str)

            # Display the current page number and total number of tickets
            current_page = (start_index // results_per_page) + 1
            total_pages = (total_tickets // results_per_page) + (1 if total_tickets % results_per_page > 0 else 0)
            self.label.config(
                text=f"Jira Ticket Management - Page {current_page} of {total_pages}, Total Tickets: {total_tickets}")

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

# Create another Tkinter root window
root2 = tk.Tk()
# Create another Jira object and pass the new root window as a parameter to its constructor
obj = Jira(master=root2)

obj.get_issues(jql = "PROJECT = PAKRASHI")
# Call the get_tickets_from_database method of the Jira object to retrieve tickets from the databas
obj.get_tickets_from_database()


# Call the get_all_jira_tickets method of the Jira object to retrieve all Jira tickets
obj.get_all_jira_tickets()



