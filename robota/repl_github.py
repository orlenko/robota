import json
import os
import subprocess

from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn
from rich.prompt import Prompt
from rich.table import Table
from slugify import slugify

from .env import CHECKOUT_DIR
from .env import GITHUB_ORG as DEFAULT_ORG
from .env import GITHUB_REPOS
from .github import get_my_prs, github_org
from .jira import get_issue
from .progress import with_progress


def ask_user_for_repos():
    repos = []
    while 1:
        repo = Prompt.ask(
            f"Which repo(s)? ({' '.join(set(GITHUB_REPOS) - set(repos))} or a different one)"
        )
        repos.extend(repo.split(" "))
        has_more = Prompt.ask("One more?", choices=["y", "n"], default="n")
        if has_more == "n":
            break
    return repos


@with_progress
def checkout_repos(workdir_path, title, repos):
    return _checkout_repos(workdir_path, title, repos)


def _checkout_repos(workdir_path, title, repos):
    if not repos:
        repos = ask_user_for_repos()

    jira_story_id = os.path.basename(workdir_path)

    branchname = f"vlad-{jira_story_id}-{slugify(title)}"

    for repo in [r for r in repos if r.strip()]:
        print(f"Checking out {github_org()}/{repo}")
        cmd = (
            f"cd {workdir_path} && "
            f"git clone git@github.com:{github_org()}/{repo}.git && "
            f"cd {repo} && "
            f"git fetch && "
            f'git checkout -B {branchname} $(git rev-parse --verify {branchname} || echo "")'
        )
        print("Running", cmd)
        result = subprocess.run(
            cmd, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE
        )
        if result.returncode != 0:
            raise Exception("Failed to clone repo or checkout branch")


@with_progress
def evaluate_workon(console, ast):
    """
    Work on a JIRA story: check out the branches and set up the workspace.

    Usage examples:
       workon TICKET-1234
       workon TICKET-1234 my-repository my-other-repository my-third-repository
    """
    jira_story_id = ast[1]
    console.print(f"Working on {ast[1]}")
    proj_slug = slugify(ast[1])
    workdir_path = os.path.join(CHECKOUT_DIR, proj_slug)

    # Fetch the story
    jira_story = get_issue(jira_story_id)

    workspace_fname = f"{workdir_path}/{proj_slug}-{slugify(jira_story.fields.summary)}.code-workspace"
    if not os.path.exists(workdir_path):
        os.makedirs(workdir_path)
        _checkout_repos(workdir_path, jira_story.fields.summary, ast[2:])
        with open(workspace_fname, "w") as f:
            json.dump(
                {
                    "folders": [
                        {"path": subfolder} for subfolder in os.listdir(workdir_path)
                    ],
                },
                f,
            )

    first_repo = os.path.join(workdir_path, [x for x in os.listdir(workdir_path) if not x.endswith('.code-workspace')][0]) # To be used later for terminal
    command = f"code {workspace_fname}"
    console.print(f"Running {command}...")
    subprocess.run(command, shell=True)
    script_path = os.path.join(os.path.dirname(__file__), 'open_terminal_at.sh')
    result = subprocess.run([script_path, first_repo], capture_output=True, text=True)
    result.check_returncode()


def evaluate_org(console, ast):
    """Get or Set the GitHub organization

    Example usage:
        org
        org my-org
    """
    if 1 < len(ast):
        github_org(ast[1])
    console.print(f"Current GitHub organization: {github_org()}")


@with_progress
def evaluate_prs(console, ast):
    """List my pull requests"""
    prs = get_my_prs()
    table = Table(title=f"My Pull Requests from {github_org()}")
    table.add_column("PR")
    table.add_column("Summary")
    for pr in prs:
        table.add_row(
            f"[link={pr.html_url}]{pr.repository.name}/{pr.number}",
            f"[link={pr.html_url}]{pr.title}",
        )
    console.print(table)
