import os
import shutil
from collections import defaultdict
from functools import wraps
from traceback import print_exc

from rich.console import Console

from robota.repl_github import evaluate_prs, evaluate_workon
from robota.repl_jira import (
    evaluate_boards,
    evaluate_list,
    evaluate_projects,
    evaluate_sprint_issues,
    evaluate_sprints,
    evaluate_unestimated,
)

from .env import CHECKOUT_DIR
from .errors import RobotaError
from .github import (
    commit_all_and_push,
    create_pull,
    get_current_branch,
    is_current_directory_clean,
)
from .jira import add_comment_to_issue, get_issue, set_issue_status

console = Console()

commands = {}


def make_command(*args):
    def decorator(func):
        for arg in args:
            commands[arg] = func

        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return decorator


def command(*args):
    """Run a shell command"""
    cmd = args[0]
    cmdargs = args[1:]
    default_handler = lambda *a: unknown_command(cmd, *a)
    try:
        return commands.get(cmd, default_handler)(*cmdargs)
    except RobotaError as rerr:
        print(f"Exiting for the following reason: {rerr}")
        return 42
    except:
        print("Unexpected error:")
        print_exc()
        return 1


def unknown_command(*args):
    """Handle unknown / unexpected commands."""
    print("Error: Unexpected command:", " ".join(args))
    help()
    return 1


@make_command("pr", "p")
def make_pr(commit_message=None, ready_for_review=False, no_jira=False):
    """Commit and push current directory, create a PR from it, add a Jira comment, and mark the Jira story as "In Progress" or "In Review", depending on arguments.

    To make a PR with a custom commit message, use the following:
    > robota pr "commit message" ready

    To create a draft PR:
    > robota pr "optional commit message'
    """
    current_branch = get_current_branch()
    if no_jira:
        if not commit_message:
            raise RobotaError("Without Jira, commit message is required")
        commit_header = commit_message
    else:
        jira_story_id = "-".join(current_branch.split("-")[1:3]).upper()
        jira_story = get_issue(jira_story_id)
        jira_story_title = jira_story.fields.summary
        commit_header = f"[{jira_story_id}] {jira_story_title}"
    push_msg = commit_header
    if commit_message:
        push_msg += f"\\n{commit_message}"
    print(f"Ready to commit and push with locals", locals())
    # return
    commit_all_and_push(push_msg)
    pr_text = (
        no_jira
        and commit_message
        or f"This PR is related to Jira story: {jira_story.permalink()}"
    )
    pr = create_pull(commit_header, pr_text, not ready_for_review)
    if not no_jira:
        jira_comment = f"PR: {pr.html_url}"
        add_comment_to_issue(jira_story_id, jira_comment)
        status = "In Review" if ready_for_review else "In Progress"
        set_issue_status(jira_story_id, status)


@make_command("help", "h")
def help():
    """Print this help screen"""
    console.print("Available commands:")
    grouped_evaluators = defaultdict(list)
    for name, fn in commands.items():
        grouped_evaluators[fn].append(name)
    for fn, names in grouped_evaluators.items():
        console.print(f"  {', '.join(names)}: {commands[names[0]].__doc__}")


@make_command("done")
def done(*_args):  # args are ignored
    """Clean up current directory and remove working files."""
    if not is_current_directory_clean():
        raise RobotaError("Cannot clean up directory that has local changes!")

    current_dir = os.getcwd()

    # Define the workspace root
    workspace_root = CHECKOUT_DIR

    if not current_dir.startswith(workspace_root):
        raise RobotaError(f"Not a workspace directory: {current_dir}")

    project_dir = current_dir[len(workspace_root) + 1 :].split(os.sep)[0]
    project_path = os.path.join(workspace_root, project_dir)

    shutil.rmtree(project_path)


@make_command("w")
def workon(*args):
    """Start working on a specific Jira story, with optional repository"""
    ast = ["w"]
    ast.extend(args)
    return evaluate_workon(console, ast)


@make_command("l")
def list_stories(*_args):
    """List Jira stories assigned to me"""
    return evaluate_list(console, [])


@make_command("p")
def list_pulls(*_args):
    """List my open PRs on GitHub"""
    return evaluate_prs(console, [])


@make_command("projects")
def list_projects():
    """List the projects from Jira"""
    return evaluate_projects(console, [])


@make_command("boards")
def list_boards():
    """List the boards from Jira"""
    return evaluate_boards(console, [])


@make_command("sprints")
def list_sprints(*args):
    """List the sprints for a board"""
    return evaluate_sprints(console, args)


@make_command("sprint-issues")
def list_sprint_issues(*args):
    """List the issues for a sprint"""
    return evaluate_sprint_issues(console, args)


@make_command("unestimated")
def list_unestimated(*args):
    """List the unestimated issues for a board"""
    return evaluate_unestimated(console, args)
