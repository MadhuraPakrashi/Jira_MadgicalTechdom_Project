import requests
import MySQLdb

# Define JIRA API URL and credentials
jira_url = 'https://pakrashi.atlassian.net/rest/api/3/search'
jira_username = 'pakrashimadhura@gmail.com'
jira_password = 'ATATT3xFfGF0YglwLzdQ5OhpAufnAomyU0mDzgxeM7rJEgMZcoLv47Bfx56EmIxysvwpecjO7KZrsCOLcHqSw_Q9DvOfQlYT-Z3PxjjjeJHVGoLND_pr91dbqxtzJDKnQqUf1zWgcG5YLwX6WpC-QuAnP4gtoCsjeHLjU-bpl1edYjfu9Cs-XAU=0B62A5EF'

# Define MySQL database connection credentials
mysql_host = 'localhost'
mysql_user = 'root'
mysql_password = 'pakrashimadhura@23'
mysql_database = 'jira'

# Define MySQL table schema
mysql_table_schema = '''
           CREATE TABLE IF NOT EXISTS jira_tickets(
                                 Key VARCHAR(50) PRIMARY KEY,
                                 summary TEXT,
                                 `status` VARCHAR(50),
                                 assignee VARCHAR(50),
                                 labels VARCHAR(50)
)
'''


# Connect to MySQL database
mysql_connection = MySQLdb.connect(
    host=mysql_host,
    user=mysql_user,
    password=mysql_password,
    database=mysql_database
)
'''mysql_cursor = mysql_connection.cursor()

# Create MySQL table if it doesn't exist
mysql_cursor.execute(mysql_table_schema)'''

# Fetch all JIRA tickets
jira_tickets = []
start_at = 0
max_results = 4
while True:
    jira_payload = {
        'jql': 'project = PAKRASHI',
        'startAt': start_at,
        'maxResults': max_results
    }
    jira_response = requests.get(
        jira_url,
        params=jira_payload,
        auth=(jira_username, jira_password)
    ).json()
    jira_tickets += jira_response['issues']
    if len(jira_response['issues']) < max_results:
        break
    start_at += max_results

# Insert JIRA tickets into MySQL table
mysql_query = '''
    INSERT INTO jira_tickets (
        Key,
        summary,
        status,
        assignee, 
        labels
    ) VALUES (
        %s, %s, %s, %s, %s
    )
'''

for ticket in jira_tickets:
    Key = ticket['key']
    Summary = ticket['fields']['summary']
    Status = str(ticket['fields']['status']['name'])
    Assignee = str(ticket['fields']['assignee']['displayName']) if ticket['fields']['assignee'] else None
    Labels = str(ticket['fields']['labels'])


    '''mysql_cursor.execute(
        mysql_query,
        (ticket_key,Summary,Status,Assignee,Labels)
    )
    mysql_connection.commit()'''

# Close MySQL database connection
mysql_cursor.close()
mysql_connection.close()
