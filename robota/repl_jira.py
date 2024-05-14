from collections import defaultdict
from rich.table import Table

from robota.progress import with_progress

from . import appstate
from .jira import (
    get_boards,
    get_my_issues,
    get_projects,
    get_sprint_issues,
    get_sprints,
    get_unestimated_issues_by_sprint,
)

status_colors = {"To Do": "grey", "In Progress": "yellow", "In Review": "green"}


def sprint_name(issue):
    sprints = issue.fields.customfield_10020
    if sprints and sprints[0].state == "active":
        return sprints[0].name
    return ""


def stories_table(title, stories, console):
    table = Table(title=title)
    table.add_column("Key")
    table.add_column("Status")
    table.add_column("Summary")
    for issue in sorted(stories, key=lambda i: int(i.key.split("-")[1]), reverse=True):
        color = status_colors.get(issue.fields.status.name, "white")
        estimate = (
            int(issue.fields.customfield_10016)
            if issue.fields.customfield_10016
            else "[unestimated]"
        )
        table.add_row(
            f"[{color}][link={issue.permalink()}]{issue.key}",
            f"[{color}]{issue.fields.status.name} - {estimate}",
            f"[{color}]{issue.fields.summary}",
        )
    console.print(table)


def sprint_table(stories, console):
    table = Table(title="Current Sprint")
    table.add_column("Key")
    table.add_column("Status")
    table.add_column("Owner")
    table.add_column("Summary")
    table.add_column("Project / Sprint")

    # Group stories by status
    status_groups = defaultdict(list)
    for issue in stories:
        status_groups[issue.fields.status.name].append(issue)

    # Add rows to the table, ordered by status and key
    known_statuses = ["To Do", "In Progress", "In Review", "Done"]
    for status in known_statuses:
        if status in status_groups:
            for issue in sorted(
                status_groups[status], key=lambda i: int(i.key.split("-")[1])
            ):
                color = status_colors.get(status, "white")
                table.add_row(
                    f"[{color}][link={issue.permalink()}]{issue.key}",
                    f"[{color}]{status}",
                    f"[{color}]{issue.fields.assignee.displayName if issue.fields.assignee else 'Unassigned'}",
                    f"[{color}]{issue.fields.summary}",
                    f"[{color}]{issue.fields.project.key} / {sprint_name(issue)}",
                )
    for issue in sorted(stories, key=lambda i: int(i.key.split("-")[1])):
        if issue.fields.status.name in known_statuses:
            continue
        status = issue.fields.status.name
        table.add_row(
            f"[link={issue.permalink()}]{issue.key}",
            f"{status}",
            f"{issue.fields.assignee.displayName if issue.fields.assignee else 'Unassigned'}",
            f"{issue.fields.summary}",
            f"{issue.fields.project.key} / {sprint_name(issue)}",
        )

    console.print(table)


@with_progress
def evaluate_list(console, ast):
    """List my JIRA stories"""
    my_issues = get_my_issues()
    appstate.set("my_issues", [i.raw for i in my_issues])
    current_sprint = [i for i in my_issues if sprint_name(i)]

    stories_table(
        "\[not in an active sprint]",
        [i for i in my_issues if not sprint_name(i)],
        console,
    )

    if current_sprint:
        stories_table(sprint_name(current_sprint[0]), current_sprint, console)


@with_progress
def evaluate_projects(console, ast):
    """List the projects from Jira"""
    projects = get_projects()
    console.print(projects)


@with_progress
def evaluate_boards(console, ast):
    """List the boards from Jira"""
    boards = get_boards()
    console.print(boards)


@with_progress
def evaluate_sprints(console, ast):
    """List the sprints for a board"""
    sprints = get_sprints(ast[0])
    console.print(sprints)


@with_progress
def evaluate_sprint_issues(console, ast):
    """List the issues for a sprint"""
    issues = get_sprint_issues(ast[0])
    # print(issues[0].raw)
    stories_table("Sprint", issues, console)


@with_progress
def evaluate_unestimated(console, ast):
    """List the unestimated issues for a board"""
    unestimated = get_unestimated_issues_by_sprint(ast[0])
    for key, issues in unestimated.items():
        stories_table(key, issues, console)
