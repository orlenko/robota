#!/bin/bash

# Check for uncommitted changes in the working directory
if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "There are uncommitted changes."
  exit 1
fi

# Get the name of the current branch
current_branch=$(git rev-parse --abbrev-ref HEAD)

# Check for unpushed commits
if [ "$(git rev-list origin/$current_branch..$current_branch)" ]; then
  echo "There are unpushed commits."
  exit 1
else
  echo "Working directory is clean and all commits are pushed."
  exit 0
fi
