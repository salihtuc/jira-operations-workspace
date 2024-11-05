import requests
import pandas as pd
import json

# Replace these variables with your Jira instance details and JQL query
jira_url = 'https://<site-name>.atlassian.net'
jql_query = '<jql query that you searched through>project = ASD AND created < 2024-10-01 ORDER BY createdDate DESC'

username = '<Your email address>'
api_token = '<Your API Token>'


# Function to get Jira search results with pagination
def get_jira_results(jira_url, jql_query, username, api_token, start_at=0, max_results=100):
    headers = {
        "Accept": "application/json",
        'Content-Type': 'application/json',
    }
    payload = json.dumps({
        "fields": [
            "*all" # You can add specific fields for better performance
        ],
        "fieldsByKeys": False,
        "jql": jql_query,
        "maxResults": max_results,
        "startAt": start_at
    })

    # auth = HTTPBasicAuth(username, api_token)

    response = requests.request(
        "POST",
        f'{jira_url}/rest/api/3/search',
        data=payload,
        headers=headers,
        auth=(username, api_token)
    )
    response.raise_for_status()  # Raise an error on bad status
    return response.json()


# Function to extract issues and handle pagination
def fetch_all_issues(jira_url, jql_query, username, api_token):
    start_at = 0
    max_results = 100
    all_issues = []

    while True:
        results = get_jira_results(jira_url, jql_query, username, api_token, start_at, max_results)
        issues = results.get('issues', [])
        all_issues.extend(issues)

        if len(issues) < max_results:
            break

        start_at += max_results

    return all_issues


def get_or_empty(value, default=""):
    if not value:
        return default

    return value
# Function to convert issues to a dataframe
def issues_to_dataframe(issues):
    if not issues:
        return pd.DataFrame()

    # Extract fields from issues
    issues_data = []
    for issue in issues:
        print(issue.get('key'))

        fields = issue.get('fields', {})
        print(fields)
        issue_data = {
            'key': issue.get('key'),
            'summary': fields.get('summary'),
            'status': fields.get('status', {}).get('name'),
            'assignee': get_or_empty(fields.get('assignee'), {"displayName": "Unassigned"}).get('displayName'), # If assignee is empty, write "Unassigned". You can edit it similar to summary, if you want to get empty values
            'reporter': get_or_empty(fields.get('reporter'), {"displayName": ""}).get('displayName'),
            'created': fields.get('created'),
            'updated': fields.get('updated'),
            '<some_custom_field>': get_or_empty(fields.get('customfield_<customfield_id>'), {"value": ""}).get('value')
        }
        issues_data.append(issue_data)

    return pd.DataFrame(issues_data)


# Main code execution
issues = fetch_all_issues(jira_url, jql_query, username, api_token)
df = issues_to_dataframe(issues)

with pd.ExcelWriter('jira_issues.xlsx') as writer:
    df.to_excel(writer, sheet_name='sheet1', engine='xlsxwriter')

# Save to Excel
# Call the function to generate comma-separated values for every 1000 records
print(issues)
print(f'{len(issues)} issues have been exported to jira_issues.xlsx')
