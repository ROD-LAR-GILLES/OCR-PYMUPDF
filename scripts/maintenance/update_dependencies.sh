#!/bin/bash

# Ensure we're in the project root
cd "$(dirname "$0")/.." || exit 1

# Check if pip-tools is installed
if ! command -v pip-compile &> /dev/null; then
    echo "Installing pip-tools..."
    pip install pip-tools
fi

# Update main requirements
echo "Updating production dependencies..."
pip-compile --upgrade --output-file requirements/requirements.txt requirements/requirements.in

# Update development requirements
echo "Updating development dependencies..."
pip-compile --upgrade --output-file requirements/requirements-dev.txt requirements/requirements-dev.in

# Check for security vulnerabilities
echo "Checking for security vulnerabilities..."
if command -v safety &> /dev/null; then
    safety check -r requirements/requirements.txt
    safety check -r requirements/requirements-dev.txt
else
    echo "Safety not installed. Install with: pip install safety"
fi

# Sync virtual environment with new requirements
echo "Syncing virtual environment..."
pip-sync requirements/requirements.txt requirements/requirements-dev.txt

echo "Dependencies updated successfully!"