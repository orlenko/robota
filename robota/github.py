import subprocess

from github import Github

from . import appstate
from .env import GITHUB_API_KEY
from .env import GITHUB_ORG as DEFAULT_ORG
from .env import GITHUB_USERNAME
from .errors import RobotaError

github = Github(GITHUB_API_KEY)


def github_org(new_org=None):
    if new_org:
        appstate.set("GITHUB_ORG", new_org)
    return appstate.get("GITHUB_ORG", DEFAULT_ORG)


def get_my_prs():
    return list(
        github.search_issues(
            f"is:open is:pr author:{GITHUB_USERNAME} archived:false user:{github_org()}"
        )
    )


def get_current_branch():
    """Get the name of the current Git branch."""
    result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True, text=True
    )
    result.check_returncode()
    return result.stdout.strip()


def get_current_repo():
    """Get the URL of the current Git repository."""
    result = subprocess.run(
        ["git", "config", "--get", "remote.origin.url"], capture_output=True, text=True
    )
    result.check_returncode()
    return result.stdout.strip()


def get_default_branch(repo):
    """Get the default (base) branch of a GitHub repository."""
    repo = github.get_repo(repo)
    return repo.default_branch


def create_pull(title, body, draft=False):
    """Create a GitHub pull request."""

    # Get current Git branch and repository
    current_branch = get_current_branch()
    repo_url = get_current_repo()

    # Parse username and repo name from URL
    username, repo_name = repo_url.split(":")[1].split("/")[0], repo_url.split("/")[
        1
    ].replace(".git", "")

    # Get repository object
    repo = github.get_repo(f"{username}/{repo_name}")

    # Get the default (base) branch for the repository
    default_branch = get_default_branch(f"{username}/{repo_name}")

    return repo.create_pull(title, body, default_branch, current_branch, draft=draft)


def commit_all_and_push(message):
    """Commit all changes in the current directory and push"""

    for command in [
        ["git", "add", "."],
        ["git", "commit", "-am", message],
        ["git", "push", "-u", "origin", get_current_branch()],
    ]:
        print("Running command", command)
        result = subprocess.run(command, capture_output=True, text=True)
        print(result.stdout.strip())
        if result.returncode != 0:
            cmd_string = " ".join(command)
            raise RobotaError(
                f"Error {result.returncode} while running command: {cmd_string}: {result.stderr.strip()}"
            )
