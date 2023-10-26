#!/bin/bash

# Check for uncommitted changes
if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "There are uncommitted changes."
  exit 1
else
  echo "Working directory is clean."
  exit 0
fi
