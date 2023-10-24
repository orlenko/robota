from jira import JIRA

from .env import JIRA_API_TOKEN, JIRA_EMAIL, JIRA_HOST

jira = JIRA(server=JIRA_HOST, basic_auth=(JIRA_EMAIL, JIRA_API_TOKEN))


def get_my_issues():
    return jira.search_issues(
        "assignee = currentUser() AND resolution = Unresolved ORDER BY priority DESC, updated DESC"
    )


def get_issue(key):
    return jira.issue(key)


def add_comment_to_issue(issue, comment_text):
    return jira.add_comment(issue, comment_text)


def set_issue_status(issue, status):
    return jira.transition_issue(issue, status)
