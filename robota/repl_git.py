import json
import os
import subprocess

from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn
from rich.prompt import Prompt
from slugify import slugify

from .jira import get_issue
from . import appstate
from .env import CHECKOUT_DIR, GITHUB_ORG, GITHUB_REPOS


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


def checkout_repos(workdir_path, title, repos):
    if not repos:
        repos = ask_user_for_repos()

    jira_story_id = os.path.basename(workdir_path)

    branchname = f"vlad-{jira_story_id}-{slugify(title)}"

    with Progress(
        SpinnerColumn(),
        TimeElapsedColumn(),
        transient=True,
    ) as progress:
        for repo in [r for r in repos if r.strip()]:
            # print(f"Checking out {GITHUB_ORG}/{repo}")
            task = progress.add_task(f"Checking out {GITHUB_ORG}/{repo}", total=1)
            cmd = (
                f"cd {workdir_path} && "
                f"git clone git@github.com:{GITHUB_ORG}/{repo}.git && "
                f"cd {repo} && "
                f"git fetch && "
                f'git checkout -B {branchname} $(git rev-parse --verify {branchname} || echo "")'
            )
            # print("Running", cmd)
            result = subprocess.run(
                cmd, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE
            )
            if result.returncode != 0:
                raise Exception("Failed to clone repo or checkout branch")
            progress.update(task, advance=1)


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
    with Progress(
        SpinnerColumn(),
        TimeElapsedColumn(),
        transient=True,
    ) as progress:
        task = progress.add_task(
            f"Getting the Jira story details for {jira_story_id}", total=1
        )
        jira_story = get_issue(jira_story_id)
        progress.update(task, advance=1)

    workspace_fname = f"{workdir_path}/{proj_slug}-{slugify(jira_story.fields.summary)}.code-workspace"
    if not os.path.exists(workdir_path):
        os.makedirs(workdir_path)
        checkout_repos(workdir_path, jira_story.fields.summary, ast[2:])
        with open(workspace_fname, "w") as f:
            json.dump(
                {
                    "folders": [
                        {"path": subfolder} for subfolder in os.listdir(workdir_path)
                    ],
                },
                f,
            )
    command = f"code {workspace_fname}"
    console.print(f"Running {command}...")
    subprocess.run(command, shell=True)
