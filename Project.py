from jira import JIRA
import pandas as pd
import csv
import MySQLdb


jiraOptions = {'server': "https://pakrashi.atlassian.net"}

jira_instance = JIRA(options=jiraOptions, basic_auth=(
    "pakrashimadhura@gmail.com", "ATATT3xFfGF0YglwLzdQ5OhpAufnAomyU0mDzgxeM7rJEgMZcoLv47Bfx56EmIxysvwpecjO7KZrsCOLcHqSw_Q9DvOfQlYT-Z3PxjjjeJHVGoLND_pr91dbqxtzJDKnQqUf1zWgcG5YLwX6WpC-QuAnP4gtoCsjeHLjU-bpl1edYjfu9Cs-XAU=0B62A5EF"))

df = pd.DataFrame()
for singleIssue in jira_instance.search_issues(jql_str = 'project =PAKRASHI'):
    df1 = pd.DataFrame(
        [{'Key': singleIssue.key,'Reporter' : singleIssue.fields.reporter.displayName,
          'Status' : singleIssue.fields.status, 'Due date' : singleIssue.fields.duedate, 'Assignee' : singleIssue.fields.assignee,
          'Priority' : singleIssue.fields.priority, 'Labels' : singleIssue.fields.labels}])
    df = pd.concat([df, df1])

df.to_csv("C:\\Users\\user\\Desktop\\MadgicalTechdom\\jira.csv", encoding="utf-8")
print(df)


mydb = MySQLdb.connect(host= 'localhost', user = 'root', password = 'pakrashimadhura@23', db = 'jiratickets')
cursor = mydb.cursor()
with open ('C:\\Users\\user\\Desktop\\MadgicalTechdom\\jira.csv','r') as csv_file:
    csvfile = csv.reader(csv_file,delimiter = ',')
    '''all_value = []
    for row in csvfile:
        value = (row[0], row[1], row[2], row[3], row[4], row[5], row[6])  # Reading the values of each row
        all_value.append(value)
query =  "INSERT INTO ticketstable (Number,Name,Reporter,Status,Due date,Assignee,Priority,Labels) VALUES (%r,%s,%s,%s,%s,%s,%s,%s)"
        #cursor.executemany(query,tuple(row))

cursor = mydb.cursor()
cursor.executemany(query,tuple(all_value))
mydb.commit()
cursor.close()'''

for index, row in df.iterrows():
    sql = "INSERT INTO ticketstable (Number,Name,Reporter,Status,Due date,Assignee,Priority,Labels) VALUES (%r, %s, %s,%s,%s,%s,%s,%s)"
    val = ( row['Key'], row['Reporter'],row['Status'],row['Due date'],row['Assignee'],
           row['Priority'],row['Labels'])
    cursor.execute(sql, val)

# commit changes to MySQL database
mydb.commit()

# close MySQL connection
mydb.close()







'''print('{}:{}:{}:{}:{}:{}:{}:{}'.format(singleIssue.key, singleIssue.fields.summary,
                             singleIssue.fields.reporter.displayName,singleIssue.fields.assignee,singleIssue.fields.status,
                             singleIssue.fields.duedate, singleIssue.fields.priority, singleIssue.fields.labels))'''