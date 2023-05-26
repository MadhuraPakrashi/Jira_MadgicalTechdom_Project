#Importing necessary libraries
import base64
import requests
import json
from requests.auth import HTTPBasicAuth
from flask import Flask, render_template, request
import mysql.connector

# Creating a Flask application instance
app = Flask(__name__)

class Jira:
    """
    This is a Jira class that provides methods to retrieve and manage Jira tickets.
    """
    def __init__(self):
        """
        This method initializes the Jira class.

        """
        # Initializing the results_per_page_entry attribute
        self.results_per_page_entry = None

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

        # Connecting to the MySQL database
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

        # Initializing page variables
        self.current_page = 1
        self.total_pages = 0



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

    def get_tickets_from_database(self, results_per_page_entry, current_page=None):
        """
        This method retrieves tickets from the MySQL database based on the page number and results per page,
        and returns them as a list.
        :param results_per_page_entry: The number of results per page to retrieve.
        :param current_page: The page number to retrieve tickets from.
        :return: A list of tickets retrieved from the database.
        """
        results_per_page = int(results_per_page_entry) if results_per_page_entry else 10

        # Getting the total number of tickets in the database
        try:
            self.mycursor.execute("SELECT COUNT(*) FROM tickets_table")
            total_tickets = self.mycursor.fetchone()[0]
        except mysql.connector.Error as e:
            print("Error while executing SQL query:", e)
            return []

        # Calculating the total number of pages and store the current page number
        self.total_pages = (total_tickets // results_per_page) + (1 if total_tickets % results_per_page > 0 else 0)
        if current_page is not None:
            self.current_page = current_page

        if results_per_page > 0:
            start_index = (self.current_page - 1) * results_per_page

            if start_index >= total_tickets:
                # If the starting index is greater than or equal to the total number of tickets, there are no more tickets to display
                return []
            else:
                try:
                    # Limiting the query to the specified page number and results per page
                    query = "SELECT * FROM tickets_table LIMIT %s, %s"
                    params = (start_index, results_per_page)
                    self.mycursor.execute(query, params)
                    myresult = self.mycursor.fetchall()
                    return myresult
                except mysql.connector.Error as e:
                    print("Error while executing SQL query:", e)
                    return []
        else:
            return []

    def get_all_jira_tickets(self):
        """
        This method retrieves all Jira tickets and inserts them into the MySQL database.
        """
        data = []
        start_at = 0
        max_results = 50
        total = 1

        while start_at < total:
            # fetching tickets for the current page
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

            # clearing data list for next page
            data.clear()

            # incrementing start_at for the next page
            start_at += max_results

        self.mycursor.close()

    def change_ticket_status(self, ticket_key, comment):
        """
        This method changes the status of a ticket from 'Open' to 'Close' and adds a comment in Jira using the API.
        :param ticket_key: The key of the ticket to update.
        :param comment: The comment to add while updating the ticket status.
        """
        # Jira API endpoint for updating an issue
        url = f"https://pakrashi.atlassian.net/rest/api/3/issue/{ticket_key}/transitions"

        # Requesting payload with the updated status and comment
        payload = json.dumps( {
            "transition": {
                "id": "41"
            }
        }
         )


        response = requests.post(url, data =payload, headers=self.header, auth=self.auth)

        if response.status_code == 204:
            print(f"Ticket {ticket_key} status updated successfully.")
        else:
            print(f"Error updating ticket status: {response.status_code} {response.text}")

    def fetch_and_store_tickets(self):
        """
        This method fetches new tickets from Jira and stores them in the MySQL database.
        """
        # Clearing existing tickets from the database
        try:
            self.mycursor.execute("TRUNCATE TABLE tickets_table")
            self.mysqldb.commit()
        except mysql.connector.Error as e:
            print("Error while truncating tickets_table:", e)

        # Fetch all Jira tickets and insert them into the database
        self.get_all_jira_tickets()


# Instantiating the Jira class
jira = Jira()


@app.route('/')
def show_tickets():
    try:
        # Getting the results_per_page_entry value from the query parameters
        results_per_page_entry = request.args.get('results_per_page_entry', 10)

        # Checking if the "Fetch Tickets" button was clicked
        if 'fetch_tickets' in request.args:
            # Fetching new tickets from Jira and store them in the database
            jira.fetch_and_store_tickets()

        # Retrieving tickets from the database using the jira object
        tickets = jira.get_tickets_from_database(results_per_page_entry, jira.current_page)

        # Rendering the template with  retrieved tickets
        return render_template('tickets.html', table_data=tickets)

    except mysql.connector.Error as e:
        print("Error while connecting to MySQL", e)

if __name__ == '__main__':
    app.debug = True
    app.run()