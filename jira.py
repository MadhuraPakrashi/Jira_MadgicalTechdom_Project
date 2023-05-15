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

        # Initialize page variables
        self.current_page = 1
        self.total_pages = 0


        # Create tkinter objects
        self.label = tk.Label(master, text="Jira Ticket Management")
        self.label.pack()

        # Added text box for entering results per page
        self.results_per_page_entry = tk.Entry(master)
        self.results_per_page_entry.pack()

        self.get_tickets_button = tk.Button(master, text="Get Tickets", command=self.get_tickets_from_database)
        self.get_tickets_button.pack()

        self.refresh_button = tk.Button(master, text="Refresh Tickets",
                                        command=lambda: [self.get_all_jira_tickets(), self.get_tickets_from_database()])
        self.refresh_button.pack()

        self.previous_page_button = tk.Button(master, text="Previous Page", command=self.show_previous_page)
        self.previous_page_button.pack(side=tk.LEFT)

        self.next_page_button = tk.Button(master, text="Next Page", command=self.show_next_page)
        self.next_page_button.pack(side=tk.RIGHT)

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
                issues.extend(data.get('issues', []))
                total = data.get('total')
                start_at += max_results
            else:
                print(f"Error fetching issues: {response.status_code} {response.text}")
                break
        return issues

    def show_previous_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.get_tickets_from_database(self.current_page)

    def show_next_page(self):
        """
        This method is triggered when the "Next Page" button is clicked.
        It updates the current page number and retrieves and displays the tickets for the next page.
        """
        self.current_page += 1  # Update the current page number
        self.get_tickets_from_database(
        self.current_page)  # Call get_tickets_from_database() with the current page number

    def get_tickets_from_database(self, current_page=None):
        """
        This method retrieves tickets from the MySQL database based on the page number and results per page,
        and displays them in the GUI window.
        :param current_page: The page number to retrieve tickets from.
        """
        results_per_page_entry_value = self.results_per_page_entry.get()
        results_per_page = int(results_per_page_entry_value) if results_per_page_entry_value else 10

        # Get the total number of tickets in the database
        self.mycursor.execute("SELECT COUNT(*) FROM tickets_table")
        total_tickets = self.mycursor.fetchone()[0]

        # Calculate the total number of pages and store the current page number
        self.total_pages = (total_tickets // results_per_page) + (1 if total_tickets % results_per_page > 0 else 0)
        if current_page is not None:
            self.current_page = current_page

        # Clear the current listbox content
        self.tickets_listbox.delete(0, tk.END)

        if results_per_page > 0:
            start_index = (self.current_page - 1) * results_per_page

            if start_index >= total_tickets:
                # If the starting index is greater than or equal to the total number of tickets, there are no more tickets to display
                self.tickets_listbox.insert(tk.END, "No more tickets to display.")
            else:
                # Limit the query to the specified page number and results per page
                self.mycursor.execute("SELECT * FROM tickets_table LIMIT %s, %s", (start_index, results_per_page))
                myresult = self.mycursor.fetchall()

                # Insert each row of data into the listbox
                for row in myresult:
                    # Join the row into a string to insert into the listbox
                    row_str = " | ".join(str(r) for r in row)
                    self.tickets_listbox.insert(tk.END, row_str)

        # Display the current page number and total number of tickets
        self.label.config(
            text=f"Jira Ticket Management - Page {self.current_page} of {self.total_pages}, Total Tickets: {total_tickets}")

    def get_all_jira_tickets(self):
        """
        This method retrieves all Jira tickets and inserts them into the MySQL database.
        """
        data = []
        start_at = 0
        max_results = 50
        total = 1

        while start_at < total:
            # fetch tickets for the current page
            url = f"{self.jira_url}?startAt={start_at}&maxResults={max_results}"
            response = requests.get(url, headers=self.header, auth=self.auth)
            tickets = json.loads(response.text)
            all_issues = tickets["issues"]
            total = tickets["total"]

            for issue in all_issues:
                date = issue["fields"]["updated"].split("T")
                created_date = issue["fields"]["created"].split("T")
                dict_obj = {"Tickets_key": issue["key"], "Title": issue["fields"]["summary"],
                            "Project_name": issue["fields"]["project"]["name"],
                            "Priority": issue["fields"]["priority"]["name"],
                            "Updated_date": date[0], "Ticket_status": issue["fields"]["status"]["name"],
                            "Creator_email": issue["fields"]["creator"]["emailAddress"],
                            "Created_date": created_date[0]}
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

            # clear data list for next page
            data.clear()

            # increment start_at for the next page
            start_at += max_results

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
obj.show_previous_page()
obj.show_next_page()
# Call the get_tickets_from_database method of the Jira object to retrieve tickets from the databas
obj.get_tickets_from_database(current_page=1)


# Call the get_all_jira_tickets method of the Jira object to retrieve all Jira tickets
obj.get_all_jira_tickets()




