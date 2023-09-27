from github import Auth, Github

from . import appstate
from .env import GITHUB_API_KEY
from .env import GITHUB_ORG as DEFAULT_ORG
from .env import GITHUB_USERNAME

g = Github(GITHUB_API_KEY)


def github_org(new_org=None):
    if new_org:
        appstate.set("GITHUB_ORG", new_org)
    return appstate.get("GITHUB_ORG", DEFAULT_ORG)


def get_my_prs():
    return list(
        g.search_issues(
            f"is:open is:pr author:{GITHUB_USERNAME} archived:false user:{github_org()}"
        )
    )
