import json
import os
import subprocess

from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn
from rich.prompt import Prompt
from slugify import slugify

from .jira import get_issue
from . import appstate
from .env import CHECKOUT_DIR, GITHUB_ORG, GITHUB_REPOS


def get_repos(workdir_path, title):
    repos = []
    while 1:
        repo = Prompt.ask(f"Which repo(s)? ({' '.join(set(GITHUB_REPOS) - set(repos))} or a different one)")
        repos.extend(repo.split(" "))
        has_more = Prompt.ask("One more?", choices=["y", "n"], default="n")
        if has_more == "n":
            break

    jira_story_id = os.path.basename(workdir_path)

    branchname = f"vlad-{jira_story_id}-{slugify(title)}"

    with Progress(
        SpinnerColumn(),
        TimeElapsedColumn(),
        transient=True,
    ) as progress:
        for repo in repos:
            task = progress.add_task(f"Checking out {GITHUB_ORG}/{repo}", total=1)
            cmd = f"cd {workdir_path} && " \
                f"git clone git@github.com:{GITHUB_ORG}/{repo}.git && " \
                f"cd {repo} && " \
                f'git checkout -B {branchname} $(git rev-parse --verify {branchname} || echo "")'
            result = subprocess.run(cmd, shell=True)
            if result.returncode != 0:
                raise Exception("Failed to clone repo or checkout branch")
            progress.update(task, advance=1)


def evaluate_workon(console, ast):
    """Work on a JIRA story: check out the branches and set up the workspace"""
    jira_story_id = ast[1]
    console.print(f"Working on {ast[1]}")
    proj_slug = slugify(ast[1])
    workdir_path = os.path.join(CHECKOUT_DIR, proj_slug)
    workspace_fname = f"{workdir_path}/{proj_slug}.code-workspace"
    if not os.path.exists(workdir_path):
        console.print(f"Fetching story and creating {workdir_path}...")
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

        os.makedirs(workdir_path)
        get_repos(workdir_path, jira_story.fields.summary)
        with open(workspace_fname, "w") as f:
            json.dump(
                {
                    "name": f"{proj_slug}: {jira_story.fields.summary}",
                    "folders": [
                        {"path": subfolder} for subfolder in os.listdir(workdir_path)
                    ],
                },
                f,
            )
    command = f"code {workspace_fname}"
    console.print(f"Running {command}...")
    subprocess.run(command, shell=True)
