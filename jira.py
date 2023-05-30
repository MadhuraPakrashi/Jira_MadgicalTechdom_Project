#Importing necessary libraries
import base64
import requests
import json
from requests.auth import HTTPBasicAuth
from flask import Flask, render_template, request, redirect
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
        #Initializing the results_per_page_entry attribute
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

        # Connecting to MySQL database
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

        #Initializing the page variables
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
            return self.get_tickets_from_database(self.results_per_page_entry, self.current_page)
        return []

    def show_next_page(self):
        self.current_page += 1
        return self.get_tickets_from_database(self.results_per_page_entry, self.current_page)

    def get_tickets_from_database(self, results_per_page_entry, current_page=None):
        try:
            if not self.mysqldb.is_connected():
                self.mysqldb.ping(reconnect=True)
                self.mysqldb = mysql.connector.connect(
                    user='root',
                    password='pakrashimadhura@23',
                    host='localhost',
                    database='jiratickets'
                )
                self.mycursor = self.mysqldb.cursor(buffered=True)
            print("Cursor connection status after reconnecting:",
                  self.mysqldb.is_connected())  # Use mysqldb instead of mycursor

            if current_page:
                offset = (current_page - 1) * results_per_page_entry
                sql = f"SELECT * FROM tickets_table LIMIT {results_per_page_entry} OFFSET {offset}"
            else:
                sql = f"SELECT * FROM tickets_table LIMIT {results_per_page_entry}"

            self.mycursor.execute(sql)
            tickets = self.mycursor.fetchall()
            return tickets

        except Exception as e:
            print("Error while retrieving tickets from the database:", e)
            return []

    def get_all_jira_tickets(self):
        """
        This method retrieves all Jira tickets and returns them as a list.
        """
        data = []
        start_at = 0
        max_results = 50
        total = 1

        while start_at < total:
            url = f"{self.jira_url}?startAt={start_at}&maxResults={max_results}"
            response = requests.get(url, headers=self.header, auth=self.auth)
            if response.status_code == 200:
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
            else:
                print(f"Error fetching issues: {response.status_code} {response.text}")
                break

            start_at += max_results

        return data

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

    def fetch_and_store_tickets(self, results_per_page_entry):
        self.results_per_page_entry = results_per_page_entry

        try:
            if not self.mysqldb.is_connected():
                self.mysqldb.ping(reconnect=True)
                self.mysqldb = mysql.connector.connect(
                    user='root',
                    password='pakrashimadhura@23',
                    host='localhost',
                    database='jiratickets'
                )
                self.mycursor = self.mysqldb.cursor(buffered=True)
            print("Cursor connection status after reconnecting:", self.mysqldb.is_connected())

            # Get the existing ticket keys from the database
            self.mycursor.execute("SELECT Tickets_key FROM tickets_table")
            existing_ticket_keys = [row[0] for row in self.mycursor.fetchall()]

            # Fetch tickets from Jira
            data = self.get_all_jira_tickets()

            # Update or insert each ticket
            for ticket in data:
                ticket_key = ticket['Tickets_key']
                if ticket_key in existing_ticket_keys:
                    # Ticket already exists in the database, update it
                    sql = """
                    UPDATE tickets_table
                    SET Title = %s, Project_name = %s, Priority = %s,
                    Updated_date = %s, Ticket_status = %s, Creator_email = %s,
                    Created_date = %s
                    WHERE Tickets_key = %s
                    """
                    val = (
                        ticket['Title'],
                        ticket['Project_name'],
                        ticket['Priority'],
                        ticket['Updated_date'],
                        ticket['Ticket_status'],
                        ticket['Creator_email'],
                        ticket['Created_date'],
                        ticket_key
                    )
                    self.mycursor.execute(sql, val)
                else:
                    # Ticket doesn't exist in the database, insert it
                    sql = """
                    INSERT INTO tickets_table (Tickets_key, Title, Project_name, Priority,
                    Updated_date, Ticket_status, Creator_email, Created_date)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    val = (
                        ticket['Tickets_key'],
                        ticket['Title'],
                        ticket['Project_name'],
                        ticket['Priority'],
                        ticket['Updated_date'],
                        ticket['Ticket_status'],
                        ticket['Creator_email'],
                        ticket['Created_date']
                    )
                    self.mycursor.execute(sql, val)

            self.mysqldb.commit()
            print("Tickets updated or inserted successfully.")

            self.mycursor.close()
            self.mysqldb.close()

            return self.get_tickets_from_database(self.results_per_page_entry, self.current_page)

        except mysql.connector.Error as e:
            print("Error while connecting to MySQL", e)

    def get_total_pages(self, results_per_page_entry):
        try:
            if not self.mysqldb.is_connected():
                self.mysqldb.ping(reconnect=True)
                self.mysqldb = mysql.connector.connect(
                    user='root',
                    password='pakrashimadhura@23',
                    host='localhost',
                    database='jiratickets'
                )
                self.mycursor = self.mysqldb.cursor(buffered=True)
            print("Cursor connection status after reconnecting:", self.mysqldb.is_connected())

            self.mycursor.execute("SELECT COUNT(*) FROM tickets_table")
            total_tickets = self.mycursor.fetchone()[0]
            total_pages = total_tickets // results_per_page_entry
            if total_tickets % results_per_page_entry != 0:
                total_pages += 1

            return total_pages

        except Exception as e:
            print("Error while calculating total pages:", e)
            return 0


# Instantiating the Jira class
jira = Jira()

@app.route('/')
def show_tickets():
    try:
        results_per_page_entry = int(request.args.get('results_per_page_entry', 10))
        current_page = int(request.args.get('page', 1))

        if request.args.get('fetch_tickets'):
            tickets = jira.fetch_and_store_tickets(results_per_page_entry)
            return redirect(request.path + f"?results_per_page_entry={results_per_page_entry}&page={current_page}")

        total_pages = jira.get_total_pages(results_per_page_entry)

        if request.args.get('previous'):
            current_page -= 1
            if current_page < 1:
                current_page = 1
            return redirect(request.path + f"?results_per_page_entry={results_per_page_entry}&page={current_page}")

        if request.args.get('next'):
            current_page += 1
            if current_page > total_pages:
                current_page = total_pages
            return redirect(request.path + f"?results_per_page_entry={results_per_page_entry}&page={current_page}")

        tickets = jira.get_tickets_from_database(results_per_page_entry, current_page)
        return render_template('tickets.html', table_data=tickets, results_per_page_entry=results_per_page_entry, current_page=current_page, total_pages=total_pages)

    except mysql.connector.Error as e:
        print("Error while connecting to MySQL", e)

if __name__ == '__main__':
    app.debug = True
    app.run()
