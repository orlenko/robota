import subprocess
from traceback import print_exc

from .errors import RobotaError
from .github import commit_all_and_push, create_pull, get_current_branch
from .jira import add_comment_to_issue, get_issue, set_issue_status


def command(*args):
    """Run a shell command"""
    print("Running command with args:", *args)
    cmd = args[0]
    cmdargs = args[1:]
    handlers = {"pr": make_pr}
    default_handler = lambda *a: unknown_command(cmd, *a)
    try:
        return handlers.get(cmd, default_handler)(*cmdargs)
    except RobotaError as rerr:
        print(f"Exiting because of {rerr}")
        return 42
    except:
        print("Unexpected error:")
        print_exc()
        return 1


def unknown_command(*args):
    """Handle unknown / unexpected commands."""
    print("Error: Unexpected command:", " ".join(args))
    return 1


def make_pr(commit_message=None, ready_for_review=False):
    """Commit and push current directory, create a draft PR or PR from it, add a Jira comment, and mark the Jira story as "in progress" or "in review", depending on arguments.

    Assume that the branch name is in the format vlad-{jira_story_id}-{slugified-title}.

    Based on the JIRA story ID, get the actual title of the story from Jira API (using get_issue from .jira module)/

    Commit current code as follows:
    > git add . && git commit -am "[{jira-story-id}] {jira-story-title}" && git push

    If a commit_message argument is provided, it is appended as a second line in the commit message:
    > git add . && git commit -am "[{jira-story-id}] {jira-story-title}\n{commit_message}" && git push

    After committing and pushing, create a draft PR or PR based on this branch (depending on ready_for_review value), using Github API. The PR description should say:
    "This PR is related to Jira story: {jira-story-link}."

    After the PR is created, copy its URL and add a comment to the Jira story:
    "PR: {pr_url_link}"

    Then, set the Jira story status to "in progress" or "in review", depending on ready_for_review value.
    """
    current_branch = get_current_branch()
    jira_story_id = current_branch.split("-")[1]
    jira_story = get_issue(jira_story_id)
    jira_story_title = jira_story.title
    commit_header = f"[{jira_story_id}] {jira_story_title}"
    commit_msg = commit_header
    if commit_message:
        commit_msg += f"\\n{commit_message}"
    commit_all_and_push(commit_message)
    pr_text = f"This PR is related to Jira story: {jira_story.permalink()}"
    pr = create_pull(commit_header, pr_text, not ready_for_review)
    jira_comment = f"PR: {pr.url}"
    add_comment_to_issue(jira_story_id, jira_comment)
    status = "In Review" if ready_for_review else "In Progress"
    set_issue_status(jira_story_id, status)
