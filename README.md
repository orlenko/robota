# Automation of Jira and Github work

Automates part of the workflow centered around Jira stories and related Github pull requests.

Main motivation: imagine that you have three work-related repos and a dozen Jira stories that each involve one or more of these repose.

A typical work on a story will involve the following steps:
 - Locate the Jira story on the storyboard, open it in a new tab
 - Figure out which repo(s) will need to change to implement the story
 - Clone those repos, check out new branch with something like `git checkout -b username-story-id-short-description`
 - After making the changes, git add, git commit, git push, and create the PR, linking it to the Jira story and duplicating the Jira story title.
 - Updating the Jira to point to the PR(s) and changing the status to "In Progress" or "In Review".
 - Cleaning up local changes, if necessary


 The `robota` script automates portions of this workflow, making it more consistent and predictable, and letting you focus on the core parts of the work.

 (The name `robota` means "work" in Ukrainian. This is also where the word "robot" comes from.)

 To use: `alias robota=/path/to/run.sh`. You will need to have python and poetry. Just do `pyenv local 3.11 && poetry install`, this should generally be enough.

Example uses:

## Command mode

```
 ❯ robota help
Available commands:
  pr: Commit and push current directory, create a draft PR or PR from it, add a Jira comment, and mark the Jira story as "In Progress" or "In Review", depending on arguments.

    To make a PR with a custom commit message, use the following:
    > robota pr "commit message" ready

    To create a draft PR:
    > robota pr "optional commit message'

  p: List my open PRs
  help, h: Print this help screen
  done: Clean up current directory and remove working files.
  w: Start working on a specific story, with optional repository
  l: List stories assigned to me


❯ robota l
⠙ 0:00:01                                                      [not in an active sprint]
┏━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Key       ┃ Status      ┃ Summary                                                                                                 ┃
┡━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ STAT-1324 │ To Do       │ Fix station unit tests so that they can run on M1                                                       │
...

```

The Jira stories are clickable links.

You can open VSCode and a shell to work on a story, by saying,

```
❯ robota w STAT-1234 my-repo-name
```

This will checkout my-repo-name into a location under `CHECKOUT_DIR` (see `./env.py` for all environment variables), and create a VSCode workspace. You can work with multiple repos that are related to a single story, in a single workspace.

Once the coding is done, you can say `robota pr` to commit your work and create a PR, updating the Jira story appropriately.

Once all work related to a story is done, saying `robota done` will remove the temporary directory.


## REPL Mode

The same tasks can be performed in an interactive REPL shell of robota. Run `robota` without arguments to start it.

```
❯ robota
robota (l/w/o/p/q/h) > l
⠦ 0:00:02                                                      [not in an active sprint]
┏━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Key       ┃ Status      ┃ Summary                                                                                                 ┃
┡━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ STAT-1324 │ To Do       │ Fix station unit tests so that they can run on M1                                                       │
...


robota (l/w/o/p/q/h) > h
Available commands:
  l: List my JIRA stories
  w:
    Work on a JIRA story: check out the branches and set up the workspace.

    Usage examples:
       workon TICKET-1234
       workon TICKET-1234 my-repository my-other-repository my-third-repository

  o: Get or Set the GitHub organization

    Example usage:
        org
        org my-org

  p: List my pull requests
  q: Quit the program
  h: Display this help message
```
