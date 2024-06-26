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


def get_projects():
    return sorted(
        [(project.name, project.key) for project in jira.projects()], key=lambda x: x[0]
    )


def get_boards():
    return sorted(
        [(board.name, board.id) for board in jira.boards()], key=lambda x: x[0]
    )


def get_sprints(board_id):
    return [
        (sprint.name, sprint.state, sprint.id)
        for sprint in jira.sprints(board_id, state="active,future")
    ]


def get_sprint_issues(sprint_id):
    return jira.search_issues(
        f"sprint = {sprint_id} AND resolution = Unresolved ORDER BY status DESC, updated DESC"
    )


def get_unestimated_issues_by_sprint(board_id):
    result = {}
    for sprint_name, _, sprint_id in get_sprints(board_id):
        for issue in get_sprint_issues(sprint_id):
            if issue.fields.customfield_10016 is None:
                result.setdefault(sprint_name, []).append(issue)
    return result
