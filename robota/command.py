from collections import defaultdict
from functools import wraps
from traceback import print_exc

from rich.console import Console

from .errors import RobotaError
from .github import commit_all_and_push, create_pull, get_current_branch
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
        print(f"Exiting because of {rerr}")
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
def make_pr(commit_message=None, ready_for_review=False):
    """Commit and push current directory, create a draft PR or PR from it, add a Jira comment, and mark the Jira story as "In Progress" or "In Review", depending on arguments.

    To make a PR with a custom commit message, use the following:
    > robota pr "commit message" ready

    To create a draft PR:
    > robota pr "optional commit message'
    """
    current_branch = get_current_branch()
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
    pr_text = f"This PR is related to Jira story: {jira_story.permalink()}"
    pr = create_pull(commit_header, pr_text, not ready_for_review)
    jira_comment = f"PR: {pr.url}"
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
