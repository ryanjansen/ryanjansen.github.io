#!/bin/bash

# Simple publish script: add, commit, and push

# Check for commit message argument, else use default
if [ -z "$1" ]; then
  msg="Update site"
else
  msg="$1"
fi

git add .
git commit -m "$msg"
git push

