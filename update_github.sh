#!/bin/bash

# Update main branch
git checkout main
git add .
git commit -m "Update main branch with latest changes"
git push origin main

# Update gh-pages branch
git checkout gh-pages
git merge main
python generate_static.py
git add .
git commit -m "Update static files for GitHub Pages"
git push origin gh-pages

# Switch back to main branch
git checkout main

echo "GitHub repository and Pages site updated successfully!"