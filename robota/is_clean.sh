#!/bin/bash

# Check for uncommitted changes in the working directory
if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "There are uncommitted changes."
  exit 1
fi

# Check for unpushed commits
if git for-each-ref --format '%(upstream:short)' $(git symbolic-ref -q HEAD) | \
   grep -q '.' && [ "$(git rev-list @{u}..)" ]; then
  echo "There are unpushed commits."
  exit 1
else
  echo "Working directory is clean and all commits are pushed."
  exit 0
fi
