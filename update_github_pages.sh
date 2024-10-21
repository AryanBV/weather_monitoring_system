#!/bin/bash

# Generate static files
python generate_static.py

# Switch to gh-pages branch
git checkout gh-pages

# Remove old files
git rm -rf .

# Move new static files to root
mv build/* .
rmdir build

# Add all files
git add .

# Commit changes
git commit -m "Update static site"

# Push to GitHub
git push origin gh-pages

# Switch back to main branch
git checkout main

echo "GitHub Pages updated successfully!"