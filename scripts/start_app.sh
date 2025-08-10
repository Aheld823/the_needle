#!/bin/bash
echo "Running full data refresh..."
python scripts/full_refresh.py

echo "Starting Dash app..."
python scripts/app.py