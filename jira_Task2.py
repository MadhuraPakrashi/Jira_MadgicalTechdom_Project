import base64
import requests
import json
from requests.auth import HTTPBasicAuth
import mysql.connector
class Jira:
    def __init__(self):
        self.jira_url = 'https://pakrashi.atlassian.net/rest/api/3/search'
        self.gmail = 'pakrashimadhura@gmail.com'
        self.jira_user = 'madhura123'
        self.jira_api_token = 'ATATT3xFfGF0LpS01iVFUs5cQ9PnB9ccQFLYg5VLRXNi-RRemdcWnRrqImgs8N-XTgFoZ0Pnjf4k-PMBUAZpJgCVdxylEQyOxcPCIHoqUZaPdqh7oeOuuU8zGMybxSzVFNfphbjv2AzWSvaEw8jjPLRPxI7TVsl6Bvtp59W1LLy1rhOJsg_xS_k=0432272D'
        self.header = {"Accept": "application/json",
                         "Content-Type": "application/json",
                         "Authorization": "Basic " + base64.b64encode(f"{self.jira_user}:{self.jira_api_token}".encode()).decode() }
        self.auth = HTTPBasicAuth(self.gmail, self.jira_api_token)
        #Connecting to MySQL database
        try:
            self.mysqldb = mysql.connector.connect(
            user= 'root',
            password = 'pakrashimadhura@23',
            host =   'localhost',
            database = 'jiratickets'
            )
            self.mycursor = self.mysqldb.cursor(buffered=True)
            self.mycursor.execute("select * from tickets_table")
            myresult = self.mycursor.fetchall()

            for x in myresult:
                print(x)

        except Exception as e:
            print("My database is not connected",e)


    #Fetching all Jira tickets
    def get_all_jira_tickets(self):
        data = []
        response = requests.request("get",self.jira_url,headers=self.header,auth=self.auth)
        tickets = json.loads(response.text)
        all_issues = tickets["issues"]

        for issue in all_issues:
            date = issue["fields"]["updated"].split("T")
            created_date = issue["fields"]["created"].split("T")
            dict_obj = { "Tickets_key": issue["key"],"Title": issue["fields"]["summary"],
                        "Project_name": issue["fields"]["project"]["name"], "Priority": issue["fields"]["priority"]["name"],
                        "Updated_date": date[0], "Ticket_status": issue["fields"]["status"]["name"],
                        "Creator_email": issue["fields"]["creator"]["emailAddress"], "Created_date": created_date[0]}
            data.append(dict_obj)


        #Inserting Jira tickets into MySQL table
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
                print('Your program has an error',e)

        #Close MySQL database connection
        self.mycursor.close()

    class Jira:
        def __init__(self):
            self.jira_url = 'https://pakrashi.atlassian.net/rest/api/3/search'
            self.gmail = 'pakrashimadhura@gmail.com'
            self.jira_user = 'madhura123'
            self.jira_api_token = 'ATATT3xFfGF0LpS01iVFUs5cQ9PnB9ccQFLYg5VLRXNi-RRemdcWnRrqImgs8N-XTgFoZ0Pnjf4k-PMBUAZpJgCVdxylEQyOxcPCIHoqUZaPdqh7oeOuuU8zGMybxSzVFNfphbjv2AzWSvaEw8jjPLRPxI7TVsl6Bvtp59W1LLy1rhOJsg_xS_k=0432272D'
            self.header = {"Accept": "application/json",
                           "Content-Type": "application/json",
                           "Authorization": "Basic " + base64.b64encode(
                               f"{self.jira_user}:{self.jira_api_token}".encode()).decode()}
            self.auth = HTTPBasicAuth(self.gmail, self.jira_api_token)

        def change_ticket_status(self, ticket_key, comment):
            url = f"https://pakrashi.atlassian.net/rest/api/3/issue/{ticket_key}/transitions"
            headers = {"Content-Type": "application/json", "Authorization": self.header["Authorization"]}

            # Get the available transitions for the ticket
            response = requests.get(url, headers=headers, auth=self.auth)
            available_transitions = response.json()["transitions"]

            # Find the transition ID for the "Close" status
            transition_id = None
            for transition in available_transitions:
                if transition["to"]["name"] == "Closed":
                    transition_id = transition["id"]
                    break

            if not transition_id:
                print("Close transition not found for the ticket")
                return

            # Create the payload for the transition request
            payload = {
                "transition": {"id": transition_id},
                "update": {
                    "comment": [{"add": {"body": comment}}]
                }
            }

            # Send the transition request
            response = requests.post(url, headers=headers, json=payload, auth=self.auth)

            if response.status_code == 204:
                print(f"Status of ticket {ticket_key} changed to Closed with comment: {comment}")
            else:
                print(f"Error changing status of ticket {ticket_key}: {response.text}")


obj = Jira()
obj.get_all_jira_tickets()






