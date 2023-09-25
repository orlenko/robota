from dotenv import dotenv_values

config = dotenv_values(".env")

JIRA_HOST = config["JIRA_HOST"]
JIRA_EMAIL = config["JIRA_EMAIL"]
JIRA_API_TOKEN = config["JIRA_API_TOKEN"]
TODOIST_API_KEY = config["TODOIST_API_KEY"]
STATE_FILE = config["STATE_FILE"]
GITHUB_ORG = config["GITHUB_ORG"]
GITHUB_REPOS = config["GITHUB_REPOS"].split(",")
CHECKOUT_DIR=config["CHECKOUT_DIR"]
