#!/bin/bash

cd /Users/kyleabrahams/Documents/GitHub/tv  # Change this to your repo path
git stash
git pull --rebase origin main
git stash pop

