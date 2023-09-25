from .env import JIRA_API_TOKEN, JIRA_EMAIL, JIRA_HOST
from jira import JIRA

jira = JIRA(server=JIRA_HOST, basic_auth=(JIRA_EMAIL, JIRA_API_TOKEN))


def get_my_issues():
    return jira.search_issues(
        "assignee = currentUser() AND resolution = Unresolved ORDER BY priority DESC, updated DESC"
    )
