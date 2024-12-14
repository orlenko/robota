import os

from dotenv import load_dotenv

load_dotenv()

JIRA_HOST = os.getenv("JIRA_HOST")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
STATE_FILE = os.getenv("STATE_FILE")
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")
GITHUB_API_KEY = os.getenv("GITHUB_API_KEY")
GITHUB_ORG = os.getenv("GITHUB_ORG")
GITHUB_REPOS = os.getenv("GITHUB_REPOS").split(",")
CHECKOUT_DIR = os.getenv("CHECKOUT_DIR")


USER_NICKNAME = os.getenv("USER_NICKNAME")
IDE_COMMAND = os.getenv("IDE_COMMAND")
